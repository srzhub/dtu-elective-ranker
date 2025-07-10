#!/usr/bin/env python3
import pandas as pd
import json
from pathlib import Path

# === Configuration ===
SUMMARY_FILE = "data_wo_proj_sem.xlsx"    # Must have: code, title, semester, count, avg_grade
GRADES_FILE  = "all_branches_results-2.csv"      # Must have: branch, RollNo, code, LetterGrade, grade

OUTPUT_DIR = Path("json_data_7sem")
OUTPUT_DIR.mkdir(exist_ok=True)

# === 1. Load data ===
df_summary = pd.read_excel(SUMMARY_FILE)
df_grades  = pd.read_csv(GRADES_FILE)

# Ensure branch uses only first 2 letters
df_grades['branch'] = df_grades['branch'].str.slice(0,2)

# === 2. Merge summary metadata into grades data ===
df = pd.merge(
    df_grades,
    df_summary[['code', 'title', 'semester', 'count', 'avg_grade']],
    on='code',
    how='left'
)

# === 3. Generate one JSON per subject code ===
for code, group in df.groupby("code"):
    # Grab the metadata from the summary
    title     = group["title"].iloc[0]
    semester  = group["semester"].iloc[0]
    count_val = group["count"].iloc[0]
    avg_grade = group["avg_grade"].iloc[0]

    # — Skip if no valid title —
    if pd.isna(title) or str(title).strip() == "":
        print(f"Skipping {code!r}: no title available")
        continue

    # Handle missing or zero count
    if pd.isna(count_val) or count_val == 0:
        count = 0
    else:
        count = int(count_val)

    # Only include specific grades
    desired_grades = [10, 9, 8, 7, 6, 5, 0]
    raw_counts = group["grade"].value_counts().to_dict()
    grade_counts = {str(g): int(raw_counts.get(g, 0)) for g in desired_grades}

    # Average GPA per branch
    branch_avg = (
        group.groupby("branch")["grade"]
        .mean()
        .round(2)
        .to_dict()
    )

    # Assemble JSON payload
    data = {
        "code": code,
        "name": title,
        "semester": semester,
        "count": count,
        "avg_grade": float(avg_grade) if not pd.isna(avg_grade) else None,
        "gradeCounts": grade_counts,
        "branchAverages": branch_avg
    }

    # Write to file
    out_path = OUTPUT_DIR / f"{code}_sem7.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {out_path}")

print(f"\nAll JSON files written to: {OUTPUT_DIR.resolve()}")
