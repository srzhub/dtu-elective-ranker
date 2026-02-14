#!/usr/bin/env python3
# captures all 5 sem subjects and has correct count as well
"""
DTU 5th Semester Parser - FIXED VERSION.

Usage:
    python parser_5sem.py -i CO-1-7.pdf -o results.json
    python parser_5sem.py -i folder -o results.json --verify CO303
"""

import pdfplumber
import re
import json
import argparse
import os
from collections import defaultdict, Counter

GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6,
    "C": 5, "P": 4, "CP": 4, "F": 0, "AB": 0
}

BRANCHES = ['CO', 'IT', 'SE', 'MC', 'EC', 'EE', 'EP', 'ME', 'EN', 'BT', 'EV', 'AE', 'PE', 'CE', 'CH']

def normalize_grade(s):
    if not s:
        return None
    g = str(s).strip().upper()
    return g if g in GRADE_POINTS else None

def is_valid_subject_code(code):
    if not code or len(code) < 3:
        return False
    code_upper = code.upper()
    if code_upper in ['TC', 'SGPA', 'SR', 'NO', 'NAME', 'STUDENT', 'FAILED', 'COURSES']:
        return False
    return bool(re.match(r'^[A-Z]{2,6}\d{2,4}[a-zA-Z]?$', code_upper))

def find_roll_numbers(text):
    if not text:
        return []
    branch_pattern = '|'.join(BRANCHES)
    pattern = r'\b(2[Kk]\d{2}/(?:' + branch_pattern + r')/\d{2,4})\b'
    matches = re.findall(pattern, str(text), re.IGNORECASE)
    return [m.upper() for m in matches]

def extract_metadata(text):
    semester, year, dept = None, None, None
    
    if m := re.search(r',\s*([IVXLCDM]+)[\s\-]*SEMESTER', text, re.I):
        semester = m.group(1)
    if m := re.search(r'HELD IN\s*(\w+\s*\d{4})', text, re.I):
        year = m.group(1)
    if m := re.search(r'Bachelor of Technology\(([^)]+)\)', text, re.I):
        dept = m.group(1).strip()
    
    return semester, year, dept

def extract_batch_from_roll(roll):
    if m := re.match(r'^2K(\d{2})/', roll, re.I):
        return "20" + m.group(1)
    return None

def extract_subjects_from_line(line):
    """Extract subjects from header line like 'CO301 : SOFTWARE ... CO303 : THEORY ...'"""
    pattern = r'\b([A-Z]{2,6}\d{2,4}[a-zA-Z]?)\s*:'
    matches = re.findall(pattern, line)
    return [m.upper() for m in matches if is_valid_subject_code(m)]

def is_subject_header_line(line):
    """Check if line is a subject header (has multiple subject codes with colons)"""
    subjects = extract_subjects_from_line(line)
    return len(subjects) >= 1

def is_table_header_line(line):
    """Check if line is table header (Sr.No Roll No. ...)"""
    return bool(re.search(r'Sr\.?\s*No|Roll\s*No', line, re.I))

def parse_pdf_correct(pdf_path, debug=False):
    """Parse PDF correctly by tracking subject context."""
    
    subjects_data = defaultdict(lambda: {
        "student_grades": {},
        "subject_code": None,
        "semester": None,
        "exam_year": None,
        "department": None,
        "batches": set()
    })
    
    all_students = set()
    global_meta = {"semester": None, "year": None, "dept": None}
    
    if debug:
        print("\nDEBUG: " + os.path.basename(pdf_path))
    
    with pdfplumber.open(pdf_path) as pdf:
        # State variables to track context across pages
        last_subjects = [] 
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            lines = [l.strip() for l in text.split('\n')]
            
            # Extract metadata
            if page_num == 1:
                sem, yr, dept = extract_metadata(text)
                global_meta["semester"] = sem or global_meta["semester"]
                global_meta["year"] = yr or global_meta["year"]
                global_meta["dept"] = dept or global_meta["dept"]
            
            current_subjects = []
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # --- CASE 1: Subject Header Line ---
                if is_subject_header_line(line):
                    current_subjects = extract_subjects_from_line(line)
                    last_subjects = current_subjects  # Update global context
                    
                    if debug:
                        print(f"  Line {i}: Found Subjects: {current_subjects}")

                    # Check next line for more subjects (sometimes headers wrap)
                    if i + 1 < len(lines) and is_subject_header_line(lines[i+1]):
                         more = extract_subjects_from_line(lines[i+1])
                         current_subjects.extend(more)
                         last_subjects = current_subjects
                         i += 1
                    
                    i += 1
                    continue

                # --- CASE 2: Table Header Line ---
                if is_table_header_line(line):
                    i += 1
                    continue

                # --- CASE 3: Student Row ---
                rolls = find_roll_numbers(line)
                if rolls:
                    roll = rolls[0]
                    all_students.add(roll)
                    batch = extract_batch_from_roll(roll)
                    
                    # Determine which subjects apply. 
                    # If we have current page subjects, use them. 
                    # If not (continuation from previous page), use last_subjects.
                    active_subjects = current_subjects if current_subjects else last_subjects
                    
                    if not active_subjects:
                        i += 1
                        continue

                    # Extract Grades
                    tokens = line.split()
                    
                    # Find where the roll number is to start reading grades after it
                    roll_pos = -1
                    for idx, t in enumerate(tokens):
                        if roll in t:
                            roll_pos = idx
                            break
                    
                    if roll_pos >= 0:
                        after_roll = tokens[roll_pos + 1:]
                        grades = []
                        
                        for token in after_roll:
                            # Stop at SGPA/CGPA (e.g., "8.20" or "TC")
                            # The fixed regex checks for decimal numbers usually ending the row
                            if re.match(r'^\d{1,2}\.\d{2}$', token): 
                                break
                            if token.upper() == "TC":
                                break
                                
                            g = normalize_grade(token)
                            if g:
                                grades.append(g)
                        
                        # Map grades to subjects
                        # We iterate based on the minimum length to avoid index errors
                        for j in range(min(len(grades), len(active_subjects))):
                            subj = active_subjects[j]
                            grd = grades[j]
                            
                            if roll not in subjects_data[subj]["student_grades"]:
                                subjects_data[subj]["student_grades"][roll] = grd
                                subjects_data[subj]["subject_code"] = subj
                                subjects_data[subj]["semester"] = global_meta["semester"]
                                subjects_data[subj]["exam_year"] = global_meta["year"]
                                subjects_data[subj]["department"] = global_meta["dept"]
                                if batch:
                                    subjects_data[subj]["batches"].add(batch)
                
                i += 1
                
    return dict(subjects_data), all_students, global_meta

def consolidate_subjects(all_pdf_data):
    consolidated = defaultdict(lambda: {
        "subject_code": None,
        "semester": None,
        "exam_year": None,
        "departments": set(),
        "batches": set(),
        "student_grades": {},
        "grade_distribution": Counter()
    })
    
    for pdf_name, (subjects_data, students, metadata) in all_pdf_data.items():
        for subj_code, data in subjects_data.items():
            cons = consolidated[subj_code]
            cons["subject_code"] = data["subject_code"]
            cons["semester"] = data["semester"] or cons["semester"]
            cons["exam_year"] = data["exam_year"] or cons["exam_year"]
            
            if data["department"]:
                cons["departments"].add(data["department"])
            cons["batches"].update(data["batches"])
            
            for roll, grade in data["student_grades"].items():
                if roll not in cons["student_grades"]:
                    cons["student_grades"][roll] = grade
                    cons["grade_distribution"][grade] += 1
    
    return dict(consolidated)

def create_output(consolidated_data, total_students):
    subject_list = []
    
    for code in sorted(consolidated_data.keys()):
        data = consolidated_data[code]
        
        if data["student_grades"]:
            grades = [GRADE_POINTS[grade] for grade in data["student_grades"].values()]
            avg = sum(grades) / len(grades)
            
            grade_dist = {grade: data["grade_distribution"][grade] 
                         for grade in ["O", "A+", "A", "B+", "B", "C", "P", "CP", "F"]}
            
            subject_list.append({
                "subject_code": data["subject_code"] or code,
                "semester": data["semester"],
                "exam_year": data["exam_year"],
                "departments": sorted(list(data["departments"])),
                "batches": sorted(list(data["batches"])),
                "total_students": len(data["student_grades"]),
                "average_grade_point": round(avg, 2),
                "grade_distribution": grade_dist,
                "pass_percentage": round((len(data["student_grades"]) - grade_dist["F"]) / len(data["student_grades"]) * 100, 2)
            })
    
    return {
        "total_students_across_all_pdfs": total_students,
        "total_subjects": len(subject_list),
        "subject_details": subject_list
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--verify", type=str)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    
    print("="*70)
    print("DTU 5th Semester Parser - FIXED")
    print("="*70)
    
    # Get files
    if os.path.isfile(args.input):
        pdf_files = [args.input]
    elif os.path.isdir(args.input):
        pdf_files = [os.path.join(args.input, f) for f in os.listdir(args.input) 
                     if f.lower().endswith('.pdf')]
    else:
        print("Error: Invalid input")
        return
    
    print(f"Found {len(pdf_files)} PDF(s)\n")
    
    # Parse
    all_pdf_data = {}
    all_unique_students = set()
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"Processing: {filename}")
        
        try:
            subjects_data, students, metadata = parse_pdf_correct(pdf_path, debug=args.debug)
            all_pdf_data[filename] = (subjects_data, students, metadata)
            all_unique_students.update(students)
            print(f"  -> {len(students)} students, {len(subjects_data)} subjects")
        except Exception as e:
            print(f"  -> FAILED: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
    
    print("\nConsolidating...")
    consolidated = consolidate_subjects(all_pdf_data)
    result = create_output(consolidated, len(all_unique_students))
    
    # Verify
    if args.verify:
        subj = args.verify.upper()
        print(f"\n{'='*70}\nVERIFICATION: {subj}\n{'='*70}")
        
        if subj in consolidated:
            data = consolidated[subj]
            print(f"Total: {len(data['student_grades'])}")
            print(f"Depts: {', '.join(sorted(data['departments']))}")
            print(f"\nGrade Distribution:")
            for grade in ["O", "A+", "A", "B+", "B", "C", "P", "CP", "F"]:
                count = data['grade_distribution'][grade]
                if count > 0:
                    pct = (count / len(data['student_grades']) * 100)
                    print(f"  {grade:3s}: {count:4d} ({pct:.1f}%)")
            
            print(f"\nFirst 30 students:")
            for roll in sorted(data['student_grades'].keys())[:30]:
                print(f"  {roll} : {data['student_grades'][roll]}")
        else:
            print("Not found. Available:")
            for s in sorted(consolidated.keys())[:40]:
                print(f"  {s} ({len(consolidated[s]['student_grades'])} students)")
    
    # Save
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Summary
    print(f"\n{'='*70}\nRESULTS\n{'='*70}")
    print(f"Students: {result['total_students_across_all_pdfs']}")
    print(f"Subjects: {result['total_subjects']}")
    
    print("\nTop 30 by enrollment:")
    for s in sorted(result['subject_details'], key=lambda x: x['total_students'], reverse=True)[:30]:
        print(f"  {s['subject_code']:12s} {s['total_students']:4d} students  "
              f"avg={s['average_grade_point']:5.2f}  pass={s['pass_percentage']:5.1f}%")
    
    print(f"\nSaved: {args.output}")

if __name__ == "__main__":
    main()