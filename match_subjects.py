#!/usr/bin/env python3
"""
match_subjects.py

Extracts subject codes and titles from a PDF legend, reads an Excel sheet
of subject codes with student counts and average grades, merges them,
and writes out a new Excel file with subject names included.
"""

import re
import pdfplumber
import pandas as pd

# === Edit these paths as needed ===
PDF_PATH    = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\subject_names.pdf"
EXCEL_PATH  = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\subject_code_averages_with_counts.xlsx"
OUTPUT_PATH = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\subject_data_with_names.xlsx"
CODE_COLUMN = "SubjectCode"  # name of the column in your Excel sheet with the codes

def extract_code_title_map(pdf_path):
    """
    Parse the PDF at pdf_path to build a DataFrame mapping cleaned codes to titles.
    """
    entries = []
    code_pattern = re.compile(r'^([A-Z]{2,3}\s*-?\d{3})\s+(.+)$')
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split('\n'):
                m = code_pattern.match(line.strip())
                if not m:
                    continue
                raw_code = m.group(1)
                title    = m.group(2).strip()
                # Normalize code: remove spaces & hyphens, uppercase
                code_clean = raw_code.replace(" ", "").replace("-", "").upper()
                entries.append((code_clean, title))
    # Build DataFrame and drop any duplicate codes (keep first occurrence)
    df_map = pd.DataFrame(entries, columns=['code', 'title'])
    df_map = df_map.drop_duplicates(subset=['code'], keep='first')
    return df_map

def read_subject_excel(excel_path, code_col):
    """
    Read the Excel sheet, normalize the codes, and add a 'code_clean' column.
    """
    df = pd.read_excel(excel_path, dtype={code_col: str})
    df['code_clean'] = (
        df[code_col]
          .str.replace(r'[\s\-]+', '', regex=True)
          .str.upper()
    )
    return df

def merge_and_export(subject_df, map_df, out_path):
    """
    Merge on the cleaned codes (now guaranteed unique in map_df) and write out.
    """
    merged = subject_df.merge(
        map_df,
        left_on='code_clean',
        right_on='code',
        how='left',
        validate='many_to_one'
    )
    # Drop helper columns
    merged = merged.drop(columns=['code_clean', 'code'])
    merged.to_excel(out_path, index=False)
    print(f"[✓] Merged data written to: {out_path}")

if __name__ == '__main__':
    print("[1/3] Extracting mapping from PDF…")
    map_df = extract_code_title_map(PDF_PATH)

    print("[2/3] Reading and normalizing codes in Excel…")
    subj_df = read_subject_excel(EXCEL_PATH, CODE_COLUMN)

    print("[3/3] Merging and exporting…")
    merge_and_export(subj_df, map_df, OUTPUT_PATH)
