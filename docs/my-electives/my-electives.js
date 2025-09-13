// Fetch data from json file
let allSubjects = []; 
fetch("syllabi.json")
  .then(res => res.json())
  .then(data => {
    allSubjects = data;
    renderElectives();
  });

  // Filter and show subjects for user to select
function filterSubjects() {
  const branch = document.getElementById("filterBranch").value;
  const semester = document.getElementById("filterSemester").value;
  const keyword = document.getElementById("searchKeyword").value.toLowerCase();

  const filtered = allSubjects.filter(subj => {
    const matchesBranch = !branch || subj.branch === branch;
    const matchesSem = !semester || subj.semester == semester;
    const matchesKeyword = subj.title.toLowerCase().includes(keyword);
    return matchesBranch && matchesSem && matchesKeyword;
  });

  const tbody = document.getElementById("searchResults");
  tbody.innerHTML = "";

  filtered.forEach(subj => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${subj.code}</td>
      <td>${subj.title}</td>
      <td>${subj.semester}</td>
      <td><button class="btn btn-sm btn-success" onclick='addElective(${JSON.stringify(subj)})'>Add</button></td>
      <td>${subj.Category}</td>

    `;
    tbody.appendChild(tr);
  });
}

//Add electives
function addElective(subject) {
  let saved = JSON.parse(localStorage.getItem("myElectives") || "[]");
  if (!saved.some(s => s.code === subject.code)) {
    saved.push(subject);
    localStorage.setItem("myElectives", JSON.stringify(saved));
    renderElectives();
  }

  showToast("Elective added!", "bg-success"); // Toast to add elective
}

//Remove Electives
function removeElective(code) {

    // if (!confirm("Remove this elective?")) return; add this later

  let saved = JSON.parse(localStorage.getItem("myElectives") || "[]");
  saved = saved.filter(s => s.code !== code);
  localStorage.setItem("myElectives", JSON.stringify(saved));
  renderElectives();

showToast("Elective removed!", "bg-danger"); // Toast to remove elective
}

// -- Show your saved electives from local storage

function renderElectives() {
  const saved = JSON.parse(localStorage.getItem("myElectives") || "[]");
  const tbody = document.getElementById("electives-body");
  const section = document.getElementById("electives-section");
  const empty = document.getElementById("empty-message");

  if (saved.length === 0) {
    section.classList.add("d-none");
    empty.classList.remove("d-none");
    return;
  }

  section.classList.remove("d-none");
  empty.classList.add("d-none");

  tbody.innerHTML = "";
  saved.forEach(subj => {
    const tr = document.createElement("tr");
    const hasPdf = subj.pdf && subj.pdf.trim() !== "";
    const syllabusIcon = hasPdf ? `
      <button class="btn btn-md btn-outline-secondary text-purple syllabus-btn" onclick="openSyllabusModal('${subj.pdf}.pdf')" title="View Syllabus">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi" viewBox="0 0 16 16">
          <path d="M5 7h6v1H5V7zm0 2h6v1H5V9z"/>
          <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 
                   2 0 0 1-2-2V2a2 2 0 0 
                   1 2-2h5.5L14 4.5zM13 5h-3.5a1 1 0 
                   0 1-1-1V1H4a1 1 0 0 0-1 
                   1v12a1 1 0 0 0 1 1h8a1 
                   1 0 0 0 1-1V5z"/>
        </svg>
      </button>` : "—";

    tr.innerHTML = `
      <td>${subj.code}</td>
      <td>${subj.title}</td>
      <td>${subj.semester}</td>
      <td>${subj.Category}</td>
      <td>${syllabusIcon}</td>
      <td><button class="btn btn-sm btn-danger" onclick="removeElective('${subj.code}')">Remove</button></td>
    `;
    tbody.appendChild(tr);

  });

}

// Open syllabus modal on the page itself (opens in new tab on mobile)

function openSyllabusModal(pdfUrl) {
  if (window.innerWidth < 768) {
    window.open(pdfUrl, "_blank");
  } else {
    const frame = document.getElementById("pdfViewerFrame");
    frame.src = pdfUrl;
    const modal = new bootstrap.Modal(document.getElementById("pdfModal"));
    modal.show();
  }
}

// -- Show toast when confirming Add or Remove

function showToast(message, color = "bg-success") {
  const toastEl = document.getElementById("liveToast");
  const toastBody = document.getElementById("toast-message");

  toastEl.classList.remove("bg-success", "bg-danger", "bg-warning");
  toastEl.classList.add(color); // apply correct color
  toastBody.textContent = message;

  const toast = new bootstrap.Toast(toastEl);
  toast.show();
}

// -- Add mandatory subjects of each sem and branch autmomatically

const branchFilter = document.getElementById("branchToggle")
const semFilter = document.getElementById("semToggle");

function updateElectivesFromFilters(){
  const newSem = parseInt(semFilter.value);
  const newBranch = branchFilter.value

  if(!newSem || !newBranch) return;

  const mandatorySubjects = allSubjects.filter(
    s => s.semester === newSem && s.branch === newBranch && s.type ==="Mandatory"
  );
  localStorage.setItem("myElectives", JSON.stringify(mandatorySubjects));
  renderElectives();
}
semFilter.addEventListener("change", updateElectivesFromFilters);
branchFilter.addEventListener("change", updateElectivesFromFilters);






// Bulk‑download all saved syllabi as a ZIP (NOT FUNCTIONAL RIGHT NOW)
async function downloadAllZipped() {
  const saved = JSON.parse(localStorage.getItem("myElectives") || "[]");
  if (saved.length === 0) {
    showToast("No electives to download", "bg-warning");
    return;
  }

  const zip = new JSZip();
  for (const subj of saved) {
    try {
      const response = await fetch(`../CS Semester/${subj.pdf}`);
;
      if (!response.ok) throw new Error(`Failed to fetch ${subj.pdf}`);
      const blob = await response.blob();
      zip.file(`${subj.code}.pdf`, blob);
    } catch (err) {
      console.error(err);
    }
  }

  const content = await zip.generateAsync({ type: "blob" });
  saveAs(
    content,
    `Syllabi_Sem${saved[0].semester}_Electives.zip`
  );
}

// Wire it up to your button
document
  .getElementById("downloadButton")
  .addEventListener("click", downloadAllZipped);
