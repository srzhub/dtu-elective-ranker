# DTUElectives.in | Academic Analytics & Elective Management

A production-grade web utility designed for 15,000+ students at **Delhi Technological University** to optimize elective selection using historical GPA analytics and automated syllabus aggregation.

**Live Application:** [https://dtuelectives.in](https://dtuelectives.in)

## 🛠️ Engineering Highlights
* **Data-Driven Ranking Engine:** Engineered a specialized interface to sort and filter multi-semester elective subjects based on average GPA distributions.
* **Client-Side State Persistence:** Developed a "My Subjects" dashboard utilizing **LocalStorage** for persistent elective tracking without requiring a backend database.
* **Dynamic Blob Management:** Integrated a bulk-export utility that dynamically generates ZIP archives of PDF syllabi on the client side for offline access.
* **Cross-Resolution Consistency:** Implemented responsive design principles to ensure a seamless experience across mobile and desktop viewports.

## 📊 Decoupled Data Pipeline
To ensure high frontend performance and maintainability, the data ingestion layer is decoupled from the presentation layer:
* **Automation Repository:** [dtu-electives-scripts](https://github.com/srzhub/dtu-electives-scripts)
* **Pipeline:** Python-based scrapers parse raw university PDF records into optimized **JSON datasets**, which are then asynchronously consumed by this frontend.

## 📂 Project Architecture
* `/json_data`: Compiled GPA analytics datasets for the 2025 academic cycle.
* `/my-electives`: Core logic for user-specific elective tracking and state persistence.
* `/svgs`: Optimized vector assets for high-DPI displays.
* `/syllabi`: Comprehensive PDF library for the CSE branch (2023 batch onwards).

## 💻 Tech Stack
* **Frontend:** Vanilla JavaScript (ES6+), Bootstrap 5, HTML5, CSS3.
* **Data Ingestion:** Python (BeautifulSoup/Pandas).
* **Hosting:** GitHub Pages / Vercel.