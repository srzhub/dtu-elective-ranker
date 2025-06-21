#!/usr/bin/env python3
"""
find_missing_subjects.py

1) Reads your merged Excel and finds all SubjectCodes with no Title.
2) Searches for each missing code in every PDF in a given folder.
3) Writes out a CSV listing, for each code, which PDFs mention it.
"""

import os
import re
import pandas as pd
import pdfplumber
from glob import glob

# === EDIT THESE PATHS ===
EXCEL_PATH     = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\subject_data_with_names.xlsx"
PDF_FOLDER     = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\Results"
OUTPUT_CSV     = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\missing_code_locations.csv"
CODE_COLUMN    = "SubjectCode"  # column name in Excel
TITLE_COLUMN   = "title"        # column name for the subject name

def load_missing_codes(excel_path):
    """
    Load the Excel and return a list of unique codes where TITLE_COLUMN is null/blank.
    """
    df = pd.read_excel(excel_path, engine='openpyxl', dtype={CODE_COLUMN:str})
    # Drop any codes that are NaN or empty, then filter where title is missing
    df = df.dropna(subset=[CODE_COLUMN])
    missing = df[df[TITLE_COLUMN].isna()][CODE_COLUMN].str.strip().unique()
    return [c for c in missing if c]

def make_search_pattern(code):
    """
    Build a regex that matches letter‑digit codes with optional spaces/hyphens.
    E.g. "IT328" → r'\bIT[\s\-]*328\b', case-insensitive.
    """
    m = re.match(r'^([A-Za-z]+)(\d+)$', code)
    if not m:
        # fallback to exact match
        return re.compile(re.escape(code), re.IGNORECASE)
    letters, numbers = m.groups()
    return re.compile(r'\b' + re.escape(letters) + r'[\s\-]*' + re.escape(numbers) + r'\b', re.IGNORECASE)

def scan_pdfs_for_codes(codes, pdf_folder):
    """
    For each code, search every PDF in pdf_folder.
    Returns a list of dicts: {'SubjectCode': code, 'FoundInPDFs': 'a.pdf;b.pdf;...'}
    """
    pdf_paths = glob(os.path.join(pdf_folder, '*.pdf'))
    results = []

    for code in codes:
        pat = make_search_pattern(code)
        found_files = []

        for pdf_path in pdf_paths:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                if pat.search(text):
                    found_files.append(os.path.basename(pdf_path))
            except Exception as e:
                print(f"  [!] Could not read {pdf_path}: {e}")

        results.append({
            CODE_COLUMN: code,
            "FoundInPDFs": ";".join(found_files) if found_files else ""
        })

    return results

def main():
    print("Loading missing subject codes from Excel…")
    codes = load_missing_codes(EXCEL_PATH)
    print(f"  → {len(codes)} codes to search for.")

    print(f"Scanning PDFs in folder: {PDF_FOLDER}")
    mapping = scan_pdfs_for_codes(codes, PDF_FOLDER)

    print(f"Writing results to CSV: {OUTPUT_CSV}")
    pd.DataFrame(mapping).to_csv(OUTPUT_CSV, index=False)
    print("Done!")

if __name__ == '__main__':
    main()
