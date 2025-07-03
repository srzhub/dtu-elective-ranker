import pandas as pd
import json
from pathlib import Path

df = pd.read_csv("all_branches_results.csv")  # or read CSV

# Test with a specific subject code
test_code = 'HU305'
sub = df[df['code'] == test_code]

grades = sub['grade'].value_counts().sort_index().astype(int).to_dict()
branch_avg = sub.groupby('branch')['grade'].mean().round(2).to_dict()

data = {
    "code": test_code,
    "grades": grades,
    "branchAverages": branch_avg,
    "totalStudents": len(sub)
}

output_folder = Path("json_data/")
output_folder.mkdir(exist_ok=True)

with open(output_folder / f"{test_code}.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"JSON created for {test_code} (without name)")
