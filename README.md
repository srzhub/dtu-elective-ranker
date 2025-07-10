# DTUElectives.in

A lightweight web application to help DTU students choose and manage electives based on historical GPA data and syllabi.

**Live Demo:** [https://dtuelectives.in](https://dtuelectives.in)

---

## Features

* **Elective GPA Ranker**
  View and sort average GPA for elective subjects across Sem I, III, V, and VII.

* **Filter and Search**
  Filter by department (CO, IT, HU, etc.), semester, or keyword.

* **Syllabus Library**
  Browse and download PDF syllabi for every year of the CSE branch (from the 2023 batch onwards).

* **My Subjects**
  Save your selected subjects and electives to a personalized list.

* **Bulk Syllabus Download**
  Export a ZIP file containing all saved subjects’ syllabi with one click.

* **Up‑to‑Date Data**
  Latest Sem V elective list added on 10 July 2025.

---

## Project Structure

CGPA Website Project/
├─ docs/
├─ CS Semester/
├─ Extra pages/
├─ json\_data/                  # Compiled JSON GPA datasets
├─ my‑electives/               # “My Subjects” feature code
├─ Scripts/
│  ├─ 1 sem scripts/           # Source data + compile scripts
│  ├─ 3 sem scripts/
│  ├─ 5 sem scripts/
│  └─ 7 sem scripts/
├─ Semester\_pages/             # Legacy static semester pages
├─ svgs/                       # Logo and icon SVG files
├─ website/
│  ├─ v1-basic-noSearch/       # Version 1: filtering & sorting only
│  └─ v2-intermediate/         # Version 2: added search and “My Subjects”
├─ favicon.ico
├─ favicon.png
├─ index.html                  # Landing page (redirect)
├─ stylesv1.css                # Global stylesheet
└─ README.md                   # This file

---

## Tech Stack

* **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
* **Data Processing:** Python (scripts in `Scripts/` generate JSON)
* **Data Storage:** JSON files in `json_data/`
* **Hosting:** GitHub Pages (dtuelectives.in)

---

## Getting Started

1. **Clone the repository**
   git clone [https://github.com/srzhub/dtu-electives.git](https://github.com/srzhub/dtu-electives.git)
   cd dtu-electives

2. **Install dependencies** (for data compilation)
   pip install -r requirements.txt

3. **Generate or update JSON data**
   Run the Python scripts in each `Scripts/<semester> scripts/` folder to regenerate the GPA datasets in `json_data/`.

4. **Run locally**
   Open `website/v2-intermediate/index.html` in your browser.

5. **Deploy to GitHub Pages**
   Push changes to the `gh-pages` branch or your configured publishing branch to update [https://dtuelectives.in](https://dtuelectives.in).

---

## Credits

Developed and maintained by Suhaib Azmi
GitHub: [https://github.com/srzhub](https://github.com/srzhub)
