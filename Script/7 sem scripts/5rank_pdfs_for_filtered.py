#!/usr/bin/env python3
import pandas as pd

'''
We did find where our codes were using '4missing_subjects.py' but it contained a lot of overlapping
subjects, so I used this script to find which pdfs contain the most unique subject codes and what 
order to search them in to make my job easier. After this step, I finally got all my data.
'''

# === CONFIGURE PATHS ===
FILTERED_EXCEL = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\7 sem scripts\subject_data_7sem_filled.xlsx"
MAPPING_CSV    = r"C:\Users\suhai\OneDrive\Desktop\cgpa website project\Script\7 sem scripts\missing_code_locations.csv"

# Column names
CODE_COL  = "code"
TITLE_COL = "title"

# 1) Load filtered Excel and get codes still missing titles
df = pd.read_excel(FILTERED_EXCEL, engine='openpyxl', dtype={CODE_COL:str})
missing_codes = df[df[TITLE_COL].isna()][CODE_COL].astype(str).str.strip().unique()

# 2) Load the existing mapping CSV and filter to just these codes
map_df = pd.read_csv(MAPPING_CSV, dtype={CODE_COL:str})
map_df = map_df[map_df[CODE_COL].isin(missing_codes)]

# 3) Build pdf → set(codes) mapping
pdf_to_codes = {}
for _, row in map_df.iterrows():
    code = row[CODE_COL]
    pdfs = (row['FoundInPDFs'] or "").split(';')
    for pdf in pdfs:
        if pdf:
            pdf_to_codes.setdefault(pdf, set()).add(code)

# 4) Greedy set cover: pick the PDF covering the most as yet uncovered codes
remaining = set(missing_codes)
visit_order = []
while remaining:
    best_pdf, best_cover = None, set()
    for pdf, codes in pdf_to_codes.items():
        cover = codes & remaining
        if len(cover) > len(best_cover):
            best_cover, best_pdf = cover, pdf
    if not best_pdf:
        break
    visit_order.append((best_pdf, best_cover))
    remaining -= best_cover

# 5) Print the result
print(f"Need to visit {len(visit_order)} PDFs in this order:\n")
for idx, (pdf, codes) in enumerate(visit_order, start=1):
    print(f"{idx}. {pdf}   (covers {len(codes)} codes)")
