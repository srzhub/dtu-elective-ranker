import pandas as pd

'''
This script was used to assign branch code to each subject. Slightly modified for 1/2nd year results, 
here we have three letter subject code AEC or VAC, eg VAC15 will have 'VAC' branch code
'''

# ─── CONFIG ───────────────────────────────────────────────
INPUT_CSV   = "subjects_with_avg_cg_3sem.csv"     # or change to your CSV filename
INPUT_XLSX  = "Dataset\compiled data in excel sheets\subjects_with_avg_cg_sem1.xlsx"    # or change to your Excel filename
OUTPUT_CSV  = "final_1sem.csv"
OUTPUT_XLSX = "final_1sem.xlsx"

CODE_COL    = "code"      # the column holding codes (e.g. "CO405")
NEW_COL     = "subject"   # the new column to create

# ─── LOAD DATA ────────────────────────────────────────────
try:
    df = pd.read_csv(INPUT_CSV, dtype={CODE_COL:str})
    print(f"Loaded data from {INPUT_CSV!r}")
except FileNotFoundError:
    df = pd.read_excel(INPUT_XLSX, dtype={CODE_COL:str})
    print(f"Loaded data from {INPUT_XLSX!r}")

# ─── COMPUTE PREFIX ───────────────────────────────────────
# Take first three characters of the code (uppercased)
df[NEW_COL] = df[CODE_COL].astype(str).str[:3].str.upper()

# ─── EXPORT ───────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
df.to_excel(OUTPUT_XLSX, index=False)

print("✅ Added column 'subject' (first two letters of code) and exported:")
print(f"   • {OUTPUT_CSV}")
print(f"   • {OUTPUT_XLSX}")
