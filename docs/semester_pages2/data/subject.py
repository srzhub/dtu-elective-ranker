import json
import re

INPUT_FILE = "semester6.json"
OUTPUT_FILE = "semester6_fixed.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for sub in data.get("subjects", []):
    if sub.get("subject_type"):
        continue

    code = sub.get("subject_code", "")
    if not code:
        continue

    match = re.match(r"[A-Za-z]{2}", code)
    if match:
        sub["subject_type"] = match.group(0).upper()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ subject_type filled where missing")
