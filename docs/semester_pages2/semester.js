console.log("semester.js loaded");

const SEM = window.SEMESTER_ID;
if (!SEM) {
  console.error("SEMESTER_ID not defined");
}

let allSubjects = [];

fetch(`data/semester${SEM}.json`)
  .then(res => res.json())
  .then(data => {
    allSubjects = data.subjects;
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
    subjects = subjects.filter(s =>
      s.subject_type === subjectFilter
    );
  }


  // Name filter (ADD HERE)
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


  // Student count filter
  // const studentFilter = document.getElementById("studentFilter").value;
  // if (studentFilter !== "all") {
  //   const minStudents = parseInt(studentFilter);
  //   subjects = subjects.filter(s => s.total_students >= minStudents);
  // }

  // Sorting
  const sortOrder = document.getElementById("sortOrder").value;
  subjects.sort((a, b) =>
    sortOrder === "asc"
      ? a.average_grade_point - b.average_grade_point
      : b.average_grade_point - a.average_grade_point
  );

  // Render
  subjects.forEach((sub, index) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${sub.subject_code}</td>
      <td>
      <a href="subject.html?sem=${SEM}&code=${sub.subject_code}" style="color:#212020;text-decoration:underline;">
        ${sub.subject_name}
      </a>
      </td>
      <td>
      ${
        sub.syllabus
        ? `
          <a 
          href="${sub.syllabus}" 
          target="_blank"
          class="syllabus-icon"
          title="View syllabus"
          >
          <i class="bi bi-file-earmark-text"></i>
          </a>
        `
        : `<span class="text-muted">—</span>`
      }
      </td>
      <td>${sub.total_students}</td>

      <td>${sub.average_grade_point.toFixed(2)}</td>


    `;

    tbody.appendChild(tr);
  });
}


// Event listeners
document.getElementById("sortOrder").addEventListener("change", renderTable);
document.getElementById("studentFilter").addEventListener("change", renderTable);
document.getElementById("nameFilter").addEventListener("input", renderTable);
document.getElementById("subjectFilter").addEventListener("change", renderTable);

// focus on desktop only
const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/.test(navigator.userAgent);
if (!isMobile) {
  document.getElementById("nameFilter").focus();
}
  
