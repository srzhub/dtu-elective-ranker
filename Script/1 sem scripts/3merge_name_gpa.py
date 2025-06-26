import pandas as pd

'''
This script matches AEC/VAC elective names from a reference Excel file ("legend") 
with corresponding subject codes in the GPA dataset.

Useful for aligning subject code–based GPA data with human-readable course names.
'''


df_grades = pd.read_excel("subject_code_averages_with_counts.xlsx")
df_names = pd.read_excel("electives_list_aec_vac_only.xlsx")

# print(df_grades.columns)
# print(df_names.columns)


df_merged = pd.merge(
    df_names,
    df_grades,
    on='code',
    how='left'
)

df_merged.to_excel("subjects_with_avg_cg.xlsx", index=False)