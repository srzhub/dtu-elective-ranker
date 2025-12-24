console.log("semester.js loaded");

const SEM = window.SEMESTER_ID;
if (!SEM) {
  console.error("SEMESTER_ID not defined");
}

let allSubjects = [];

fetch(`data/semester${SEM}.json`)
  .then(res => res.json())
  .then(data => {
    allSubjects = data.subjects.map((s, idx) => ({
      ...s,
      __index: idx
    }));

    // FORCE default sort state
    const sortSelect = document.getElementById("sortOrder");
    if (sortSelect) sortSelect.value = "none";

    renderTable();
  })
  .catch(err => console.error("JSON load failed", err));


function renderTable() {
  const tbody = document.getElementById("semesterTableBody");
  tbody.innerHTML = "";

  let subjects = [...allSubjects];

  // ----- Subject / Branch filter -----
  const subjectFilter = document.getElementById("subjectFilter").value;
  if (subjectFilter !== "all") {
    subjects = subjects.filter(s => s.subject_type === subjectFilter);
  }

  // ----- Name filter -----
  const nameQuery = document
    .getElementById("nameFilter")
    .value
    .toLowerCase()
    .trim();

  if (nameQuery !== "") {
    subjects = subjects.filter(s =>
      s.subject_name.toLowerCase().includes(nameQuery)
    );
  }

  // ----- Sorting (ONLY if selected) -----
  const sortOrder = document.getElementById("sortOrder").value;

  if (sortOrder === "asc" || sortOrder === "desc") {
    subjects.sort((a, b) => {
      const aVal = a.average_grade_point ?? -Infinity;
      const bVal = b.average_grade_point ?? -Infinity;

      return sortOrder === "asc"
        ? aVal - bVal
        : bVal - aVal;
    });
  } else {
    // Default: original JSON order
    subjects.sort((a, b) => a.__index - b.__index);
  }

  // ----- Render -----
  subjects.forEach((sub, index) => {
    const tr = document.createElement("tr");

    const avgGp =
      typeof sub.average_grade_point === "number"
        ? sub.average_grade_point.toFixed(2)
        : "—";

    const totalStudents =
      typeof sub.total_students === "number"
        ? sub.total_students
        : "—";

    const slotText =
  Array.isArray(sub.slots) && sub.slots.length > 0
    ? sub.slots.join(", ")
    : "—";

  const hasData =
  typeof sub.total_students === "number" ||
  typeof sub.average_grade_point === "number" ||
  (sub.grade_distribution &&
    Object.keys(sub.grade_distribution).length > 0);



    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${sub.subject_code || "—"}</td>
      <td>
        ${
          hasData
            ? `
              <a href="subject.html?sem=${SEM}&code=${sub.subject_code}"
                style="color:#212020;text-decoration:underline;">
                ${sub.subject_name}
              </a>
            `
            : `
              <span class="text" title="No detailed data available">
                ${sub.subject_name}
              </span>
            `
        }
      </td>

      <td>
        ${
          sub.syllabus
            ? `
              <a href="${sub.syllabus}" 
                 target="_blank"
                 class="syllabus-icon"
                 title="View syllabus">
                <i class="bi bi-file-earmark-text"></i>
              </a>
            `
            : `<span class="text-muted">—</span>`
        }
      </td>
      <td>${totalStudents}</td>
      <td>${slotText}</td>
      <td>${avgGp}</td>
    `;

    tbody.appendChild(tr);
  });
}


// Event listeners
document.getElementById("sortOrder").addEventListener("change", renderTable);
document.getElementById("studentFilter")?.addEventListener("change", renderTable);
document.getElementById("nameFilter").addEventListener("input", renderTable);
document.getElementById("subjectFilter").addEventListener("change", renderTable);

// Desktop focus
const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/.test(
  navigator.userAgent
);
if (!isMobile) {
  document.getElementById("nameFilter").focus();
}
