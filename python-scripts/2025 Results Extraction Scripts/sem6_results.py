#!/usr/bin/env python3
# best one so far for 6 sem and containa consolidated for all pdfs and counting of grades but not tested enough

"""
DTU Result Parser - Batch processing for multiple PDFs.
Processes entire folder and creates consolidated subject-wise statistics.

Usage:
    python parser_2k22.py -i results_folder -o consolidated.json
    python parser_2k22.py -i results_folder -o consolidated.json --verify CO302
"""

import pdfplumber
import re
import json
import argparse
import os
from collections import defaultdict, Counter

GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6,
    "C": 5, "P": 4, "F": 0, "AB": 0
}

BRANCHES = ['CO', 'IT', 'SE', 'MC', 'EC', 'EE', 'EP', 'ME', 'EN', 'BT', 'EV', 'AE', 'PE', 'CE', 'CH']

def normalize_grade(s):
    """Normalize grade string."""
    if not s:
        return None
    g = str(s).strip().upper().replace(" ", "")
    return g if g in GRADE_POINTS else None

def is_valid_grade(s):
    """Check if string is a valid grade."""
    return normalize_grade(s) is not None

def is_valid_subject_code(code):
    """Check if code is a valid subject code."""
    if not code or len(code) < 3:
        return False
    code_upper = code.upper()
    
    if code_upper in ['TC', 'SGPA', 'SR', 'NO', 'NAME', 'STUDENT', 'FAILED', 'COURSES']:
        return False
    
    return bool(re.match(r'^[A-Z]{2,6}\d{2,4}[a-zA-Z]?$', code_upper))

def find_roll_numbers(text):
    """Find 2K22 format roll numbers."""
    if not text:
        return []
    
    branch_pattern = '|'.join(BRANCHES)
    pattern = r'\b(2[Kk]\d{2}/(?:' + branch_pattern + r')/\d{2,4})\b'
    matches = re.findall(pattern, str(text), re.IGNORECASE)
    
    return [m.upper() for m in matches]

def extract_metadata(text):
    """Extract semester, year, department."""
    semester = None
    year = None
    dept = None
    
    m_sem = re.search(r',\s*([IVXLCDM]+)[\s\-]*SEMESTER', text, re.I)
    if m_sem:
        semester = m_sem.group(1)
    
    m_year = re.search(r'HELD IN\s*(\w+\s*\d{4})', text, re.I)
    if m_year:
        year = m_year.group(1)
    
    m_dept = re.search(r'Bachelor of Technology\(([^)]+)\)', text, re.I)
    if m_dept:
        dept = m_dept.group(1).strip()
    
    return semester, year, dept

def extract_batch_from_roll(roll):
    """Extract batch from roll number."""
    m = re.match(r'^2K(\d{2})/', roll, re.I)
    if m:
        return "20" + m.group(1)
    return None

def is_descriptive_line(line):
    """Check if line is a descriptive header (not actual data)."""
    if ':' in line:
        if re.search(r'[A-Z]{2,6}\d{2,4}[a-zA-Z]?\s*:\s*[A-Z\s]{10,}', line, re.I):
            return True
    return False

def parse_table_row(row, current_header, all_students, subjects_data, page_num, global_meta):
    """Parse a single table row and extract student data."""
    
    rolls = []
    for cell in row:
        if cell:
            rolls.extend(find_roll_numbers(cell))
    
    if not rolls:
        return
    
    row_text = ' '.join([str(c or '') for c in row])
    
    if is_descriptive_line(row_text):
        return
    
    row_subjects = []
    for cell in row:
        if cell:
            cell_str = str(cell).strip()
            codes = re.findall(r'\b([A-Z]{2,6}\d{2,4}[a-zA-Z]?)\b', cell_str)
            for code in codes:
                if is_valid_subject_code(code):
                    code_upper = code.upper()
                    if code_upper not in row_subjects:
                        row_subjects.append(code_upper)
    
    clean_row_subjects = []
    for subj in row_subjects:
        if not re.search(subj + r'\s*:', row_text):
            clean_row_subjects.append(subj)
    
    if clean_row_subjects:
        subjects_in_row = clean_row_subjects
    elif current_header:
        subjects_in_row = [s[0] for s in current_header]
    else:
        return
    
    for roll in rolls:
        all_students.add(roll)
        batch = extract_batch_from_roll(roll)
        
        grades_in_row = []
        for cell in row:
            if cell and not find_roll_numbers(cell):
                for line in str(cell).split('\n'):
                    if is_valid_grade(line):
                        grades_in_row.append(normalize_grade(line))
        
        if len(grades_in_row) >= len(subjects_in_row):
            for i, subj_code in enumerate(subjects_in_row):
                if i < len(grades_in_row):
                    grade = grades_in_row[i]
                    
                    if roll not in subjects_data[subj_code]["student_grades"]:
                        subjects_data[subj_code]["student_grades"][roll] = grade
                        subjects_data[subj_code]["subject_code"] = subj_code
                        subjects_data[subj_code]["semester"] = global_meta["semester"]
                        subjects_data[subj_code]["exam_year"] = global_meta["year"]
                        subjects_data[subj_code]["department"] = global_meta["dept"]
                        if batch:
                            subjects_data[subj_code]["batches"].add(batch)

def parse_single_pdf(pdf_path):
    """Parse a single PDF file."""
    
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
    
    with pdfplumber.open(pdf_path) as pdf:
        current_header = []
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            
            if page_num == 1 or not global_meta["semester"]:
                sem, yr, dept = extract_metadata(text)
                global_meta["semester"] = sem or global_meta["semester"]
                global_meta["year"] = yr or global_meta["year"]
                global_meta["dept"] = dept or global_meta["dept"]
            
            try:
                tables = page.extract_tables(table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 3,
                })
                
                for table in (tables or []):
                    if not table or len(table) < 2:
                        continue
                    
                    first_row = table[0]
                    first_row_text = ' '.join([str(c or '') for c in first_row]).upper()
                    
                    is_header = ('ROLL' in first_row_text or 'SR.NO' in first_row_text) and 'SGPA' in first_row_text
                    
                    if is_header:
                        new_header = []
                        for idx, cell in enumerate(first_row):
                            if cell:
                                cell_str = str(cell).strip()
                                if not is_descriptive_line(cell_str):
                                    codes = re.findall(r'\b([A-Z]{2,6}\d{2,4}[a-zA-Z]?)\b', cell_str)
                                    for code in codes:
                                        if is_valid_subject_code(code):
                                            new_header.append((code.upper(), idx))
                        
                        if new_header:
                            current_header = new_header
                        
                        data_rows = table[1:]
                    else:
                        data_rows = table
                    
                    for row in data_rows:
                        parse_table_row(row, current_header, all_students, subjects_data, 
                                      page_num, global_meta)
            except:
                pass
    
    return dict(subjects_data), all_students, global_meta

def consolidate_subjects(all_pdf_data):
    """Consolidate data from multiple PDFs."""
    
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
            
            # Merge student grades (avoid duplicates)
            for roll, grade in data["student_grades"].items():
                if roll not in cons["student_grades"]:
                    cons["student_grades"][roll] = grade
                    cons["grade_distribution"][grade] += 1
    
    return dict(consolidated)

def create_consolidated_output(consolidated_data, total_students):
    """Create final consolidated JSON output."""
    
    subject_list = []
    
    for code in sorted(consolidated_data.keys()):
        data = consolidated_data[code]
        
        if data["student_grades"]:
            grades = [GRADE_POINTS[grade] for grade in data["student_grades"].values()]
            avg = sum(grades) / len(grades)
            
            # Grade distribution
            grade_dist = {}
            for grade in ["O", "A+", "A", "B+", "B", "C", "P", "F"]:
                grade_dist[grade] = data["grade_distribution"][grade]
            
            subject_list.append({
                "subject_code": data["subject_code"] or code,
                "semester": data["semester"],
                "exam_year": data["exam_year"],
                "departments": sorted(list(data["departments"])),
                "batches": sorted(list(data["batches"])),
                "total_students": len(data["student_grades"]),
                "average_grade_point": round(avg, 2),
                "grade_distribution": grade_dist,
                "pass_percentage": round((len(data["student_grades"]) - grade_dist["F"]) / len(data["student_grades"]) * 100, 2) if len(data["student_grades"]) > 0 else 0
            })
    
    return {
        "total_students_across_all_pdfs": total_students,
        "total_subjects": len(subject_list),
        "subject_details": subject_list
    }

def main():
    parser = argparse.ArgumentParser(description="DTU Batch Result Parser")
    parser.add_argument("-i", "--input", required=True, help="Input PDF file or folder")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file")
    parser.add_argument("--verify", type=str, help="Verify specific subject")
    args = parser.parse_args()
    
    print("="*70)
    print("DTU Batch Result Parser")
    print("="*70 + "\n")
    
    # Determine if input is file or folder
    pdf_files = []
    if os.path.isfile(args.input):
        pdf_files = [args.input]
    elif os.path.isdir(args.input):
        pdf_files = [os.path.join(args.input, f) for f in os.listdir(args.input) 
                     if f.lower().endswith('.pdf')]
    else:
        print("Error: Input must be a PDF file or directory")
        return
    
    if not pdf_files:
        print("Error: No PDF files found")
        return
    
    print("Found " + str(len(pdf_files)) + " PDF file(s)\n")
    
    # Parse all PDFs
    all_pdf_data = {}
    all_unique_students = set()
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print("Processing: " + filename + "...", end=" ")
        
        try:
            subjects_data, students, metadata = parse_single_pdf(pdf_path)
            all_pdf_data[filename] = (subjects_data, students, metadata)
            all_unique_students.update(students)
            print("OK (" + str(len(students)) + " students, " + str(len(subjects_data)) + " subjects)")
        except Exception as e:
            print("FAILED - " + str(e))
    
    print("\nConsolidating data...")
    consolidated = consolidate_subjects(all_pdf_data)
    result = create_consolidated_output(consolidated, len(all_unique_students))
    
    # Verification mode
    if args.verify:
        subj = args.verify.upper()
        print("\n" + "="*70)
        print("VERIFICATION: " + subj)
        print("="*70)
        
        if subj in consolidated:
            data = consolidated[subj]
            print("Total students: " + str(len(data['student_grades'])))
            print("Departments: " + ", ".join(sorted(data['departments'])))
            print("Batches: " + ", ".join(sorted(data['batches'])))
            print("\nGrade Distribution:")
            for grade in ["O", "A+", "A", "B+", "B", "C", "P", "F"]:
                count = data['grade_distribution'][grade]
                if count > 0:
                    pct = (count / len(data['student_grades']) * 100)
                    print("  " + grade.ljust(3) + ": " + str(count).rjust(4) + " (" + str(round(pct, 1)) + "%)")
        else:
            print("Subject not found!")
            print("Available: " + ", ".join(sorted(consolidated.keys())[:20]))
    
    # Save output
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    # Summary
    print("\n" + "="*70)
    print("CONSOLIDATED RESULTS")
    print("="*70)
    print("Total unique students: " + str(result['total_students_across_all_pdfs']))
    print("Total subjects: " + str(result['total_subjects']))
    
    print("\nTop Subjects by Enrollment:")
    sorted_subj = sorted(result['subject_details'], 
                        key=lambda x: x['total_students'], 
                        reverse=True)[:20]
    
    for s in sorted_subj:
        dept_str = ", ".join(s['departments'][:2])
        if len(s['departments']) > 2:
            dept_str += "..."
        
        print("  " + s['subject_code'].ljust(12) + 
              str(s['total_students']).rjust(4) + " students  " +
              "avg=" + str(s['average_grade_point']).ljust(5) + 
              " pass=" + str(s['pass_percentage']).rjust(5) + "%  " +
              "(" + dept_str + ")")
    
    print("\n" + "="*70)
    print("Grade Distribution Summary:")
    print("="*70)
    
    # Calculate overall grade distribution
    total_grade_dist = Counter()
    total_grades = 0
    
    for subj in result['subject_details']:
        for grade, count in subj['grade_distribution'].items():
            total_grade_dist[grade] += count
            total_grades += count
    
    for grade in ["O", "A+", "A", "B+", "B", "C", "P", "F"]:
        count = total_grade_dist[grade]
        pct = (count / total_grades * 100) if total_grades > 0 else 0
        bar = "#" * int(pct / 2)
        print(grade.ljust(3) + ": " + str(count).rjust(5) + " (" + 
              str(round(pct, 1)).rjust(5) + "%) " + bar)
    
    print("\nSaved: " + args.output)
    print("\nTo verify a subject: python parser_2k22.py -i folder -o output.json --verify CO302")

if __name__ == "__main__":
    main()