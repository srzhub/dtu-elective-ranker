//SEM 1 script

let subjectData = []; //this will hold all the data

fetch('../json_data/sem1_data.json')
.then( response =>{
    if(!response.ok){
        throw new Error("Network response was not OK");
    }
    return response.json()
})
.then( data=> {
    subjectData = data;
    console.log("data loaded: ", subjectData);
    buildTable(subjectData);
})
.catch(error =>{
    console.error("There was a problem fetching data: " , error)
})


let currentFilter = null
let currentSort = null
let currentSearch = ''



// Read value of sorting column
document.getElementById("order").addEventListener("change", function(){
  currentSort = this.value || null
  changeTable();
})

// Read value of filtering column
document.getElementById("subject").addEventListener("change", function(){
  currentFilter = this.value || null
  changeTable();
})

document.getElementById("searchInput").addEventListener("input", function(){
  currentSearch = this.value.toLowerCase();
  changeTable();
})



  // Function to change table, either sort or filter or both.
function changeTable(){
  var table = document.getElementById("1_sem_table");
  table.innerHTML = ''
  changedData = subjectData.slice()

  if(currentSort){
    if(currentSort === "asc"){
      changedData = changedData.sort( (a,b) => parseFloat(a.grade) - parseFloat(b.grade))
    }
    else{
      changedData = changedData.sort( (a,b) => parseFloat(b.grade) - parseFloat(a.grade))
    }
  }

  if(currentFilter){
    changedData = changedData.filter((el) => el.subject === currentFilter)
  }

  if(currentSearch){
    changedData = changedData.filter( (el) => 
    el.title.toLowerCase().includes(currentSearch) ||
    el.code.toLowerCase().includes(currentSearch)
  );

  }

  buildTable(changedData)
}

  function buildTable(data){
    var table = document.getElementById("1_sem_table");
    table.innerHTML = ''

    for(var i = 0; i< data.length; i++ ){
      const row = document.createElement("tr");
      row.innerHTML =
        `<tr>
                  <td>${i+1}</td>
                  <td>${data[i].code}</td>
                  <td>${data[i].title}</td>
                  <td>${data[i].grade}</td>
                </tr>`;

      table.appendChild(row);
    }
  }