const params = new URLSearchParams(window.location.search);
const sem = parseInt(params.get("sem"))
const branch = params.get("branch") || "CO"

document.getElementById("page-title").textContent = `Semester ${sem} Subjects - ${branch}`

document.getElementById("elective-text").textContent = `View all the open electives for ${sem} semester`


fetch('sem_cs.json')
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

    buildTable(mandatorySub, "mandatory-table");

    if(electiveSub.length !== 0){
         buildTable(electiveSub, "elective-table");
    }
    else{
        document.getElementById("elective-section").textContent = ''; // If no elective subjects
                                                                      // remove the table  
    }

})
.catch(error =>{
    console.error("There was a problem fetching data: " , error)
})




// Function to build the table
  function buildTable(data,id){
    var table = document.getElementById(id);
    table.innerHTML = ''

    

    for(var i = 0; i< data.length; i++ ){
      const row = document.createElement("tr");
      const hasPdf = data[i].pdf && data[i].pdf.trim() !== "";
      row.innerHTML =
        `<tr>
                  <td>${i+1}</td>
                  <td>${data[i].code}</td>
                  <td>${data[i].title}</td>
                  <td>${data[i].MTE}</td>
                  <td>${data[i].ETE}</td>
      <td>

        ${hasPdf ? `
          <button class="btn btn-sm btn-outline-secondary ms-2" 
                  onclick="openSyllabusModal('${data[i].pdf}')"
                  title="View Syllabus">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                 class="bi" viewBox="0 0 16 16">
              <path d="M5 7h6v1H5V7zm0 2h6v1H5V9z"/>
              <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 
                       2 0 0 1-2-2V2a2 2 0 0 
                       1 2-2h5.5L14 4.5zM13 5h-3.5a1 1 0 
                       0 1-1-1V1H4a1 1 0 0 0-1 
                       1v12a1 1 0 0 0 1 1h8a1 
                       1 0 0 0 1-1V5z"/>
            </svg>
          </button>
        ` : ""}
      </td>

                
                </tr>`;

      table.appendChild(row);
    }



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