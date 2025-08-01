const params = new URLSearchParams(window.location.search);
const sem = parseInt(params.get("sem"))
const branch = (params.get("branch") || "CO").toLowerCase();

document.getElementById("page-title").textContent =
 `Semester ${sem} Subjects - ${branch}`

document.getElementById("elective-text").textContent = 
`View all the open electives for ${sem} semester`


fetch(`LQ_JSONS/${branch}.json`) 
.then( response =>{
    if(!response.ok){
        throw new Error("Network response was not OK");
    }
    return response.json()
})
.then( data=> {
    semesterData = data;
    console.log("data loaded: ",semesterData);
    let filteredData = semesterData.filter((s) => s.semester === sem) 

    let mandatorySub = filteredData.filter((s) => s.type === "Mandatory")
    let electiveSub = filteredData.filter((s) => s.type === "Elective")

    buildTable(mandatorySub, "mandatory-section", "Mandatory Subjects");

    if(electiveSub.length !== 0){
         buildTable(electiveSub, "elective-section", "Department Electives");
    }
    else{
        document.getElementById("elective-section").textContent = ''; // If no elective subjects
                                                                      // remove the table  
    }

})
.catch(error =>{
    console.error("There was a problem fetching data: " , error)
})

// decide what columns to include in each branch
const branchColumnConfig = {
  co:      { MTE: true, ETE: true, Credits: false },
  it:      { MTE: false, ETE: false, Credits: true },
  se:      { MTE: false, ETE: false, Credits: false },
  mce:     { MTE: true, ETE: false, Credits: true },
  me:     { MTE: true, ETE: true, Credits: false },
  ae:     { MTE: true, ETE: true, Credits: false },
  mc:     { MTE: true, ETE: true, Credits: false },
  ep:     { MTE: false, ETE: false, Credits: false },
  ec:     { MTE: false, ETE: false, Credits: false },
  bt:     { MTE: false, ETE: false, Credits: false },
  ce:     { MTE: true, ETE: true, Credits: false },
  default: { MTE: true, ETE: true, Credits: true }
};


// Function to build the table
  function buildTable(subjects,id,name){
    var section = document.getElementById(id);
    section.innerHTML = ''

    const bcg = branchColumnConfig[branch] || branchColumnConfig.default;

    const hasMTE = bcg.MTE
    const hasETE = bcg.ETE
    const hasCredits = bcg.Credits

    // build header
    let thead = `
    <tr>
      <th>#</th>
      <th>Code</th>
      <th>Title</th>
      ${hasMTE ? "<th>MTE</th>" : ""}
      ${hasETE ? "<th>ETE</th>" : ""}
      ${hasCredits ? "<th>Credits</th>" : ""}
      <th>Syllabus</th>
    `;

    // build body
  let tbody = subjects.map((s, i) => {
    const hasPdf = s.pdf && s.pdf.trim() !== "";
    return `
      <tr>
        <td>${i + 1}</td>
        <td>${s.code}</td>
        <td>${s.title}</td>
        ${hasMTE ? `<td>${s.MTE || "-"}</td>` : ""}
        ${hasETE ? `<td>${s.ETE || "-"}</td>` : ""}
        ${hasCredits ? `<td>${s.credits || "-"}</td>` : ""}
        <td>
          ${hasPdf ? `
            <button class="btn btn-sm btn-outline-secondary" onclick="openSyllabusModal('${s.pdf}')"> 
            <i class="bi bi-file-earmark-text text-purple"></i>
            </button>
            ` : "—"}
        </td>
      </tr>`;
  }).join("");  

    section.innerHTML = `
    <h2 class="fw-medium fs-3 ms-2 mt-1">${name}</h2>
    <div  class="table-responsive" >
  <table class="table table-hover table-borderless  custom-table ">
  <thead class="table-header">${thead}</thead>
  <tbody>                     ${tbody} </tbody>

    </table>
    </div>  
    `
    
    }

// Function to open pdf viewer Modal




function openSyllabusModal(pdfUrl) {
  const frame = document.getElementById("pdfViewerFrame");
  frame.src = pdfUrl;

if (window.innerWidth < 768) {
  window.open(pdfUrl, "_blank");
} else {
  // show modal
    const modal = new bootstrap.Modal(document.getElementById("pdfModal"));
  modal.show();
}


}

// Change semester function
document.getElementById("semToggle").value = sem; // set selected option

document.getElementById("semToggle").addEventListener("change", (e) => {
  const newSem = parseInt(e.target.value);
  const newParams = new URLSearchParams(window.location.search);
  newParams.set("sem", newSem);

  // Preserve branch param
  newParams.set("branch", branch);

  // Redirect to updated URL
  window.location.search = newParams.toString();
});


// Function to open the open electives for the semester
document.getElementById("open-elective-button").addEventListener("click",()=>{
    if(sem === 1 || sem === 2){
        window.location.href = "../Semester_pages/semester1.html"
    }
    else if(sem === 3 || sem === 4){
        window.location.href = "../Semester_pages/semester3.html"
    }
     else if(sem === 5 || sem === 6){
        window.location.href = "../Semester_pages/semester5.html"
    }
    else if(sem === 7 || sem === 8){
        window.location.href = "../Semester_pages/semester7.html"
    }
})