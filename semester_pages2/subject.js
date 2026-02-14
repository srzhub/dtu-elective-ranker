const params = new URLSearchParams(window.location.search);
const sem = params.get("sem");
const code = params.get("code");

const dataFile = `data/semester${sem}.json`;

fetch(dataFile)
  .then(res => res.json())
  .then(data => {

    const subject = data.subjects.find(
      s => s.subject_code === code
    );

    if (!subject) {
      document.body.innerHTML = "<h3>Subject not found</h3>";
      return;
    }

    // ----- BASIC INFO -----
    document.getElementById("subjectTitle").innerText =
      `${subject.subject_name} (${subject.subject_code})`;

    document.getElementById("avgGp").innerText =
      subject.average_grade_point != null
        ? subject.average_grade_point.toFixed(2)
        : "N/A";

    document.getElementById("passPercent").innerText =
      subject.pass_percentage + "%";

    document.getElementById("students").innerText =
      subject.total_students;

    const examYearEl = document.getElementById("examYear");

    if (
      subject.exam_year &&
      subject.exam_year.toString().toLowerCase() !== "unknown"
    ) {
      examYearEl.innerText = `Exam Year: ${subject.exam_year}`;
      examYearEl.style.display = "inline";
    } else {
      examYearEl.style.display = "none";
    }




    // ---------- DEPARTMENTS / BRANCHES ----------
const deptContainer = document.getElementById("departmentsContainer");
deptContainer.innerHTML = "";

subject.departments.forEach(dept => {
  const badge = document.createElement("span");
  badge.className = "badge bg-white border text-dark me-2 mb-2";
  badge.innerText = dept;
  deptContainer.appendChild(badge);
});


    // ----- CHART LOGIC -----

    const gradeOrder = ["O", "A+", "A", "B+", "B", "C", "P", "F"];

    const labels = [];
    const values = [];

    gradeOrder.forEach(grade => {
      if (subject.grade_distribution[grade] !== undefined) {
        labels.push(grade);
        values.push(subject.grade_distribution[grade]);
      }
    });

    const ctx = document.getElementById("gradeChart");

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Number of Students",
          data: values,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.raw} students`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        }
      }
    });

  })
  .catch(err => {
    console.error("Failed to load subject data", err);
  });
