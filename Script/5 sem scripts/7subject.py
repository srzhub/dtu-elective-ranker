import pandas as pd

'''
This script was used to assign branch code to each subject. Eg CO405 will have branch code 'CO'
'''

# ─── CONFIG ───────────────────────────────────────────────
INPUT_CSV   = "subject_data_5sem_final.csv"     # or change to your CSV filename
INPUT_XLSX  = "subject_data_5sem_final.xlsx"    # or change to your Excel filename
OUTPUT_CSV  = "data_with_subject_prefix.csv"
OUTPUT_XLSX = "data_with_subject_prefix.xlsx"

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
# Take first two characters of the code (uppercased)
df[NEW_COL] = df[CODE_COL].astype(str).str[:2].str.upper()

# ─── EXPORT ───────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
df.to_excel(OUTPUT_XLSX, index=False)

print("✅ Added column 'subject' (first two letters of code) and exported:")
print(f"   • {OUTPUT_CSV}")
print(f"   • {OUTPUT_XLSX}")
