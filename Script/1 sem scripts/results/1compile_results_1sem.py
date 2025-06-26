import os
import glob
import re
import pdfplumber
import pandas as pd
from collections import defaultdict

'''


This is a modified version of the original `compile_results.py` script tailored for 5-semester data.

It compiles all subjects across students, then filters the data to retain only those subjects 
with 'AEC' or 'VAC' in their names — typically electives.

Letter grades are mapped to GPA scores during processing.

'''



# ─── CONFIG ──────────────────────────────────────────────────────

GRADE_MAP = {
    'O': 10, 'A+': 9, 'A': 8, 'B+': 7,
    'B': 6, 'C': 5, 'D': 4, 'P': 4,
    'F': 0, 'Fail': 0, 'Absent': 0
}

# Columns to ignore (metadata only)
SKIP_COLS = {
    'Sr.No', 'RollNo.', 'NameofStudent', 'Nameof\nStudent',
    'SGPA', 'TC', 'FailedCourses', 'Failed\nCourses'
}

# ─── HELPERS ─────────────────────────────────────────────────────

def parse_header(cell_text):
    """
    Given a header cell string, returns (code, full_name).
    Supports:
      - "CODE\\nFull Subject Name"
      - "CODE – Full Subject Name"
      - "CODE - Full Subject Name"
    """
    if not isinstance(cell_text, str):
        return None, None

    # Try two-line format
    lines = [l.strip() for l in cell_text.splitlines() if l.strip()]
    if len(lines) >= 2 and re.match(r'^[A-Za-z0-9]+$', lines[0]):
        return lines[0], " ".join(lines[1:])

    # Try single-line "CODE – Name"
    m = re.match(r'^([A-Za-z0-9]+)\s*[–-]\s*(.+)$', cell_text.strip())
    if m:
        return m.group(1), m.group(2)

    # Fallback: treat entire cell as code only
    return cell_text.strip(), ""

# ─── CORE EXTRACTION ─────────────────────────────────────────────

def extract_from_pdf(pdf_path):
    """
    Extracts a tidy DataFrame from one PDF:
      - Branch (filename without .pdf)
      - RollNo, StudentName
      - SubjectCode, SubjectName, LetterGrade, NumericGrade
      - SGPA, TotalCredits, FailedCourses
    """
    branch = os.path.splitext(os.path.basename(pdf_path))[0]
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                df = pd.DataFrame(table[1:], columns=table[0])
                if df.shape[0] < 1:
                    continue

                # Parse and filter headers
                header_info = {}
                for raw_col in df.columns:
                    code, name = parse_header(raw_col)
                    if code and code not in SKIP_COLS and code not in GRADE_MAP:
                        header_info[raw_col] = (code, name)

                # Identify metadata columns
                roll_col = next((c for c in df.columns if 'Roll' in c), None)
                name_col = next((c for c in df.columns if 'Name' in c), None)
                sgpa_col = next((c for c in df.columns if c.strip()=='SGPA'), None)
                tc_col   = next((c for c in df.columns if c.strip()=='TC'), None)
                fail_col = next((c for c in df.columns if 'Failed' in c), None)

                # Iterate each student row
                for _, row in df.iterrows():
                    roll = row[roll_col] if roll_col else None
                    stud = row[name_col]  if name_col  else None
                    sgpa = row[sgpa_col]  if sgpa_col  else None
                    tc   = row[tc_col]    if tc_col    else None
                    fails= row[fail_col]  if fail_col  else None

                    # One record per subject
                    for raw_col, (code, subj_name) in header_info.items():
                        letter = str(row[raw_col]).strip()
                        if letter in GRADE_MAP:
                            records.append({
                                'Branch'      : branch,
                                'RollNo'      : roll,
                                'StudentName' : stud,
                                'SubjectCode' : code,
                                'SubjectName' : subj_name,
                                'LetterGrade' : letter,
                                'NumericGrade': GRADE_MAP[letter],
                                'SGPA'        : sgpa,
                                'TotalCredits': tc,
                                'FailedCourses': fails
                            })

    return pd.DataFrame.from_records(records)

# ─── MAIN ────────────────────────────────────────────────────────

def main():
    pdf_files = glob.glob("*.pdf")
    if not pdf_files:
        print("❗ No PDF files found in this directory.")
        return

    all_dfs = []
    for pdf in pdf_files:
        print(f"→ Processing {pdf} …")
        df = extract_from_pdf(pdf)
        all_dfs.append(df)

    master = pd.concat(all_dfs, ignore_index=True)

    # Filtering using a regex mask to only keep AEC and VAC subjects

    elective_regex = r'^(AEC|VAC)\d{1,3}$' 

    mask = master['SubjectCode'].str.match(elective_regex, case=False)

    master = master[mask]

    # Export to CSV & Excel
    master.to_csv("all_branches_results.csv", index=False)
    master.to_excel("all_branches_results.xlsx", index=False)
    print("✅ Exported:")
    print("   • all_branches_results.csv")
    print("   • all_branches_results.xlsx")

if __name__ == "__main__":
    main()
