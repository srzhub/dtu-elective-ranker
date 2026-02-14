# DTUElectives.in | Academic Analytics & Elective Management

DTUElectives.in is a data-driven utility designed for the 15,000+ students at **Delhi Technological University**. It assists in elective selection by synthesizing historical GPA analytics and automating syllabus management.

**Live Application:** [https://dtuelectives.in](https://dtuelectives.in)

---

## Impact & Data Recency

* **User Adoption:** Successfully served over **4,800 unique users** across two consecutive academic semesters.
* **Latest Datasets:** Includes the most recent GPA records for **Semesters 5, 6, and 7** (concluded immediately prior to the current 2026 cycle), providing the most relevant historical benchmarks for current students.
* **Target Scope:** Current datasets are optimized for the **2025 academic cycle**, covering all departments including CS, IT, HU etc.

---

## User Guide

### 1. GPA Ranking & Filtering
* Navigate to the specific semester page to view the **Elective GPA Ranker**.
* Use the search interface to filter subjects by department (e.g., CO, IT, HU).
* Subjects can be sorted by average GPA to identify historically high-scoring electives based on student performance data.

### 2. "My Subjects" & Local Persistence
* Select the "Add" button to save an elective to your personalized list.
* The system utilizes **LocalStorage**, ensuring your selections persist across browser sessions without requiring a backend account.


---

## Repository Structure

| Directory/File | Technical Function |
| :--- | :--- |
| `/json_data` | Compiled GPA analytics datasets (JSON) consumed by the frontend. |
| `/my-electives` | Logic for client-side state management and elective tracking. |
| `/syllabi` | Latest PDF library for all branch syllabi (Based on the New Education Policy). |
| `/svgs` | Optimized vector assets for high-DPI displays. |
| `index.html` | Entry point; handles client-side routing and rendering. |

---

## Developer Documentation

### Data Ingestion Pipeline
To maintain a high-performance frontend, the data processing is handled by a dedicated standalone repository:
* **Source Repository:** [dtu-electives-scripts](https://github.com/srzhub/dtu-electives-scripts)
* **Workflow:** Python-based scrapers (BeautifulSoup/Pandas) parse raw university PDFs into optimized JSON. These datasets are then hosted in the `/json_data` folder for asynchronous fetch calls.


---

## Tech Stack

* **Frontend:** Vanilla JavaScript (ES6+), Bootstrap 5, HTML5, CSS3.
* **Data Engineering:** Python (Scraping/Transformation).
* **Infrastructure:** GitHub Pages, Vercel.