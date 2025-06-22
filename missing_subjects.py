#!/usr/bin/env python3
"""
recursive_search_missing_subjects.py

Same as before, but:
 • Recursively walks PDF_FOLDER to find all .pdf files
 • Prints each PDF path as it loads
 • Shows a final count so you can verify it actually found them
"""

import os
import re
import pandas as pd
import pdfplumber

# === CONFIGURE THESE PATHS ===
EXCEL_PATH   = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\subject_data_with_names2.xlsx"
PDF_FOLDER   = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\Results"
OUTPUT_CSV   = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\missing_code_locations.csv"

# Column names in your Excel
CODE_COLUMN  = "SubjectCode"
TITLE_COLUMN = "title"

def load_missing_codes(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl', dtype={CODE_COLUMN:str})
    df = df.dropna(subset=[CODE_COLUMN])
    missing = df[df[TITLE_COLUMN].isna()][CODE_COLUMN].astype(str).str.strip().unique()
    return [c for c in missing if c]

def clean_text(s: str) -> str:
    return re.sub(r'[\s\-]+', '', s).upper()

def load_pdf_texts(pdf_folder):
    """
    Recursively find all PDFs under pdf_folder, read & clean them.
    Returns dict { filename: cleaned_text }
    """
    texts = {}
    for root, _, files in os.walk(pdf_folder):
        for fname in files:
            if not fname.lower().endswith('.pdf'):
                continue
            full = os.path.join(root, fname)
            print(f"→ Loading PDF: {full}")
            try:
                with pdfplumber.open(full) as pdf:
                    raw = "\n".join(page.extract_text() or "" for page in pdf.pages)
            except Exception as e:
                print(f"   [!] Failed to read {fname}: {e}")
                continue
            texts[full] = clean_text(raw)
    print(f"[✔] Total PDFs loaded: {len(texts)}")
    return texts

def match_codes_to_pdfs(codes, pdf_texts):
    rows = []
    cleaned_codes = {c: clean_text(c) for c in codes}
    for orig, cc in cleaned_codes.items():
        found = [os.path.basename(path) for path, txt in pdf_texts.items() if cc in txt]
        rows.append({CODE_COLUMN: orig, "FoundInPDFs": ";".join(found)})
    return rows

def main():
    print("1) Loading missing SubjectCodes…")
    codes = load_missing_codes(EXCEL_PATH)
    print(f"   → {len(codes)} codes without titles")

    print("\n2) Scanning PDFs (recursively)…")
    pdf_texts = load_pdf_texts(PDF_FOLDER)

    print("\n3) Matching codes to PDFs…")
    mapping = match_codes_to_pdfs(codes, pdf_texts)

    print(f"\n4) Writing CSV to {OUTPUT_CSV}")
    pd.DataFrame(mapping).to_csv(OUTPUT_CSV, index=False)
    print("✅ Done! Open the CSV to see which PDFs contain each missing code.")

if __name__ == "__main__":
    main()
