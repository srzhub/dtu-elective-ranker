import pandas as pd
import re

'''
Since there where many overlapping subjects from 5 sem, we merged them to get most of the subject 
names.
'''

# ─── USER CONFIGURATION ────────────────────────────────────────

# Paths to your Excel files
FILE_5SEM  = "subject_data_with_names_5sem.xlsx"
FILE_7SEM  = "subject_data_with_names.xlsx"      # your half-empty 7th-sem file
OUTPUT     = "subject_data_7sem_filled.xlsx"

# Column names
CODE_COL  = "code"
NAME_COL  = "title"

# Pattern to detect if a string is basically the code again
# e.g. matches CO301, EE415, etc.
CODE_RE = re.compile(r'^[A-Z]{2,}\d{2,}$')

# ─── LOAD DATA ─────────────────────────────────────────────────

# 5th sem fully-filled
df5 = pd.read_excel(FILE_5SEM, dtype={CODE_COL:str})
# 7th sem partially filled
df7 = pd.read_excel(FILE_7SEM, dtype={CODE_COL:str, NAME_COL:str})

# Strip whitespace
df7[CODE_COL] = df7[CODE_COL].str.strip()
df7[NAME_COL] = df7[NAME_COL].fillna("").astype(str).str.strip()

# Build a lookup dict from 5th-sem
name_lookup = dict(zip(df5[CODE_COL].str.strip(), df5[NAME_COL].astype(str).str.strip()))

# ─── FILL MISSING NAMES ────────────────────────────────────────

def should_fill(code, name):
    # Fill if name is empty or exactly equals the code or looks like a code
    if not name:
        return True
    if name.upper() == code.upper():
        return True
    if CODE_RE.match(name):
        return True
    return False

filled_names = []
for idx, row in df7.iterrows():
    code = row[CODE_COL].strip()
    name = row[NAME_COL].strip()
    if should_fill(code, name):
        # look up in df5; if missing in lookup, leave blank
        new_name = name_lookup.get(code, "")
        filled_names.append(new_name)
    else:
        filled_names.append(name)

# Assign back
df7[NAME_COL] = filled_names

# ─── SAVE OUTPUT ───────────────────────────────────────────────

df7.to_excel(OUTPUT, index=False)
print(f"✅ 7th-sem names filled (where appropriate) and saved to {OUTPUT!r}")
