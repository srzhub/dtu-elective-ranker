import pandas as pd

'''
This script calculates the average GPA for each elective subject (AEC/VAC).

The resulting dataset provides valuable insight for students during course registration, 
helping them make informed decisions when choosing electives.
'''



# ─── CONFIG ────────────────────────────────────────────────

# Input filenames (choose whichever you have)
INPUT_CSV  = "all_branches_results.csv"
INPUT_XLSX = "all_branches_results.xlsx"

# Output filenames
OUTPUT_CSV  = "subject_code_averages_with_counts.csv"
OUTPUT_XLSX = "subject_code_averages_with_counts.xlsx"

# ─── LOAD DATA ─────────────────────────────────────────────

try:
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded data from {INPUT_CSV!r}")
except FileNotFoundError:
    df = pd.read_excel(INPUT_XLSX)
    print(f"Loaded data from {INPUT_XLSX!r}")

# Ensure the grade column is numeric
df['NumericGrade'] = pd.to_numeric(df['NumericGrade'], errors='coerce')

# ─── COMPUTE AVERAGES & COUNTS ─────────────────────────────

agg_df = (
    df
    .groupby('SubjectCode', as_index=False)
    .agg(
        StudentCount=('NumericGrade', 'count'),
        AverageNumericGrade=('NumericGrade', 'mean')
    )
)

# Round the average
agg_df['AverageNumericGrade'] = agg_df['AverageNumericGrade'].round(3)

# Sort by descending average
agg_df = agg_df.sort_values('AverageNumericGrade', ascending=False)

# ─── EXPORT RESULTS ────────────────────────────────────────

agg_df.to_csv(OUTPUT_CSV, index=False)
agg_df.to_excel(OUTPUT_XLSX, index=False)

print("✅ Exported subject‑code averages with counts to:")
print(f"   • {OUTPUT_CSV}")
print(f"   • {OUTPUT_XLSX}")
