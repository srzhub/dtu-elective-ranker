#!/usr/bin/env python3
import pdfplumber
import re
import json
import argparse
import os
from collections import defaultdict, Counter

# --- Configuration ---
GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6,
    "C": 5, "P": 4, "F": 0, "AB": 0
}

# Regex to find Roll Numbers (e.g., 2K22/CO/522 or 2K21/AE/13)
# Matches standard format and variations
ROLL_NO_PATTERN = r'(2K\d{2}/[A-Z]{2,3}/\d{1,4})'

# Regex to find Subject Codes (e.g., CO302, IT328a, HU302a)
# Looks for 2-4 letters, followed by 3 digits, optionally followed by a letter
SUBJECT_CODE_PATTERN = r'\b([A-Z]{2,4}\d{3}[a-zA-Z]?)\b'

def get_grade_point(grade):
    """Converts grade letter to point value."""
    if not grade: return None
    # Clean grade (sometimes credits appear in cell like 'A+\n4' or 'A+ 4')
    # We split by newline or space and take the first part
    parts = str(grade).split()
    if not parts: return None
    g = parts[0].strip().upper()
    
    # Handle cases where grade is attached to newline
    if '\n' in str(grade):
        g = str(grade).split('\n')[0].strip().upper()

    return GRADE_POINTS.get(g)

def extract_metadata(text):
    """Extracts Semester, Batch/Year info from the first page text."""
    meta = {"semester": "Unknown", "exam_year": "Unknown", "department": "Unknown"}
    if not text: return meta
    
    # Find Semester
    sem_match = re.search(r'([IVX]+)-SEMESTER', text)
    if sem_match: meta['semester'] = sem_match.group(1)
    
    # Find Exam Year (e.g., "MAY 2025")
    year_match = re.search(r'HELD IN\s+([A-Z]+\s+\d{4})', text, re.IGNORECASE)
    if year_match: meta['exam_year'] = year_match.group(1).upper()

    # Find Department (e.g. Bachelor of Technology (Mathematics & Computing))
    dept_match = re.search(r'Bachelor of Technology\s*\(([^)]+)\)', text, re.IGNORECASE)
    if dept_match: meta['department'] = dept_match.group(1).strip()
    
    return meta

def is_header_row(row_text):
    """Determines if a row serves as a header based on content."""
    # It's a header if it contains "Roll No" OR if it contains multiple Subject Codes
    if "Roll No" in row_text or "Name of Student" in row_text:
        return True
    
    # Count subject codes in the row
    codes = re.findall(SUBJECT_CODE_PATTERN, row_text)
    # If we find 2 or more subject codes, it's likely a header row
    if len(codes) >= 2:
        return True
    return False

def parse_header_row(row):
    """
    Analyzes a header row to map column indices to Subject Codes.
    Returns: {col_index: 'CO302', col_index_2: 'CO304', ...}
    """
    header_map = {}
    for idx, cell in enumerate(row):
        if not cell: continue
        # Clean cell text
        cell_text = str(cell).replace('\n', ' ').strip()
        
        # Check if cell contains a subject code
        # We iterate all matches in the cell, but usually one cell = one subject in header
        matches = re.findall(SUBJECT_CODE_PATTERN, cell_text)
        for subj_code in matches:
            # Filter out false positives
            if subj_code not in ['SGPA', 'TC', 'MOOC'] and not subj_code.startswith('2K'):
                header_map[idx] = subj_code
                break # Map this column to this subject
            elif "MOOC" in cell_text and "MOOC" not in header_map.values():
                 header_map[idx] = "MOOC306" # Assuming standard code if generic text found
                 
    return header_map

def process_pdf(pdf_path, debug=False):
    results = []
    global_metadata = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        # 1. Extract Global Metadata from Page 1
        if len(pdf.pages) > 0:
            first_page_text = pdf.pages[0].extract_text()
            global_metadata = extract_metadata(first_page_text)

        # State to track headers across pages
        active_header_map = {}

        if debug: print(f"Processing {os.path.basename(pdf_path)} ({len(pdf.pages)} pages)...")

        for page_num, page in enumerate(pdf.pages):
            # Extract tables. 
            # 'vertical_strategy': 'lines' is best for these specific grids.
            # 'intersection_tolerance': 5 helps when lines aren't perfectly touching.
            tables = page.extract_tables(table_settings={
                "vertical_strategy": "lines", 
                "horizontal_strategy": "lines",
                "intersection_y_tolerance": 5
            })

            for table in tables:
                if not table: continue
                
                for row in table:
                    # Create a text representation of the row for regex checks
                    # Convert None to "" and join
                    clean_cells = [str(c).strip() if c else "" for c in row]
                    row_text = " ".join(clean_cells)

                    # 1. Check if this is a Header Row
                    if is_header_row(row_text):
                        new_map = parse_header_row(row)
                        if new_map:
                            active_header_map = new_map
                            if debug: print(f"  [Pg {page_num+1}] Header found: {list(active_header_map.values())}")
                        continue

                    # 2. Check if this is a Student Result Row
                    # It must contain a Roll Number regex match
                    roll_match = re.search(ROLL_NO_PATTERN, row_text)
                    
                    if roll_match and active_header_map:
                        roll_no = roll_match.group(1)
                        
                        # Calculate Batch (e.g. 2K22 -> 2022)
                        try:
                            batch_yr = "20" + roll_no.split('/')[0][2:]
                        except:
                            batch_yr = "Unknown"

                        # Iterate columns based on the active header map
                        for col_idx, subject_code in active_header_map.items():
                            if col_idx < len(row):
                                raw_val = row[col_idx]
                                if not raw_val: continue
                                
                                # Grade extraction logic
                                # Sometimes grade is "A+\n4.00" or just "A"
                                grade = str(raw_val).split('\n')[0].strip().upper()
                                
                                if grade in GRADE_POINTS:
                                    results.append({
                                        "subject_code": subject_code,
                                        "roll_no": roll_no,
                                        "grade": grade,
                                        "batch": batch_yr,
                                        "department": global_metadata.get('department', 'Unknown'),
                                        "semester": global_metadata.get('semester', 'Unknown'),
                                        "exam_year": global_metadata.get('exam_year', 'Unknown')
                                    })

    return results

def consolidate_data(all_raw_results):
    """
    Transforms flat list of grade entries into the specific hierarchical JSON format requested.
    """
    # Helper to initialize subject structure
    subject_map = {} 

    for entry in all_raw_results:
        s_code = entry['subject_code']
        
        if s_code not in subject_map:
            subject_map[s_code] = {
                "subject_code": s_code,
                "semester": entry['semester'],
                "exam_year": entry['exam_year'],
                "departments": set(),
                "batches": set(),
                "grades": [], # List of grade points for avg calc
                "grade_counts": Counter(),
                "total_students": 0
            }
        
        # Update Sets
        subject_map[s_code]["departments"].add(entry['department'])
        subject_map[s_code]["batches"].add(entry['batch'])
        
        # Update Stats
        grade_point = GRADE_POINTS[entry['grade']]
        subject_map[s_code]["grades"].append(grade_point)
        subject_map[s_code]["grade_counts"][entry['grade']] += 1
        subject_map[s_code]["total_students"] += 1

    # Final Formatting
    output_list = []
    
    for s_code, data in subject_map.items():
        # Calculate Average
        if data["total_students"] > 0:
            avg_gp = round(sum(data["grades"]) / data["total_students"], 2)
            
            # Calculate Pass % (Fail is F or AB/Absent)
            failed_count = data["grade_counts"]["F"] + data["grade_counts"].get("AB", 0)
            pass_count = data["total_students"] - failed_count
            pass_pct = round((pass_count / data["total_students"]) * 100, 2)
        else:
            avg_gp = 0.0
            pass_pct = 0.0

        # Ensure grade_distribution has all keys even if 0
        dist_fixed = {k: data["grade_counts"].get(k, 0) for k in ["O", "A+", "A", "B+", "B", "C", "P", "F"]}

        output_list.append({
            "subject_code": data["subject_code"],
            "semester": data["semester"],
            "exam_year": data["exam_year"],
            "departments": sorted(list(data["departments"])),
            "batches": sorted(list(data["batches"])),
            "total_students": data["total_students"],
            "average_grade_point": avg_gp,
            "grade_distribution": dist_fixed,
            "pass_percentage": pass_pct
        })

    # Sort by Subject Code
    return sorted(output_list, key=lambda x: x['subject_code'])

def main():
    parser = argparse.ArgumentParser(description="DTU V3 Parser (Robust Table Support)")
    parser.add_argument("-i", "--input", required=True, help="PDF file or Folder")
    parser.add_argument("-o", "--output", required=True, help="Output JSON path")
    parser.add_argument("--debug", action="store_true")
    
    args = parser.parse_args()

    all_extracted_data = []

    # Get list of files
    files = []
    if os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith('.pdf')]
    else:
        files = [args.input]

    print(f"Found {len(files)} PDFs to process.")

    for f in files:
        try:
            data = process_pdf(f, args.debug)
            all_extracted_data.extend(data)
            print(f"  -> {os.path.basename(f)}: Extracted {len(data)} records.")
        except Exception as e:
            print(f"  -> ERROR processing {f}: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()

    # Consolidate
    final_json = consolidate_data(all_extracted_data)
    
    # Save
    with open(args.output, 'w') as f:
        json.dump(final_json, f, indent=2)
    
    print(f"\nSuccessfully saved data for {len(final_json)} subjects to {args.output}")

if __name__ == "__main__":
    main()