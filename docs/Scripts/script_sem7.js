//SEM 5 script

let subjectData = []; //this will hold all the data

//Fetching JSON data
fetch('../json_data/sem7_data3.json')
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
// Read value of search column
document.getElementById("searchInput").addEventListener("input", function(){
  currentSearch = this.value.toLowerCase();
  changeTable();
})



  // Function to change table, either sort, search or filter.
function changeTable(){
  var table = document.getElementById("7_sem_table");
  table.innerHTML = ''
  changedData = subjectData.slice()

  //Sort
// Assume currentSort is "asc" or "desc"
if (currentSort) {
  changedData.sort((a, b) => {
    // pick a sentinel so empty grades always compare as the *smallest*
    // when sorting desc (so they end up last), and as the *largest*
    // when sorting asc (so they also end up last).
    const sentinelA = (a.grade === "" || a.grade == null)
      ? (currentSort === "asc" ? Infinity : -Infinity)
      : parseFloat(a.grade);
    const sentinelB = (b.grade === "" || b.grade == null)
      ? (currentSort === "asc" ? Infinity : -Infinity)
      : parseFloat(b.grade);

    // now do normal numeric compare
    if (currentSort === "asc") {
      return sentinelA - sentinelB;
    } else {
      return sentinelB - sentinelA;
    }
  });
}


  //Filter
  if(currentFilter){
    changedData = changedData.filter((el) => el.subject === currentFilter)
  }

  //Search
  if(currentSearch){
    changedData = changedData.filter( (el) => 
    el.title.toLowerCase().includes(currentSearch) ||
    el.code.toLowerCase().includes(currentSearch)
  );

  }

  buildTable(changedData)
}

  // Function to build our table
  function buildTable(data){
    var table = document.getElementById("7_sem_table");
    table.innerHTML = ''

    for(var i = 0; i< data.length; i++ ){
      const row = document.createElement("tr");
      row.innerHTML =
        `<tr>
                  <td>${i+1}</td>
                  <td>${data[i].code}</td>
                  <td>${data[i].title}</td>
                  <td>${data[i].slot}</td>
                  <td>${data[i].remark}</td>
                  <td>${data[i].grade}</td>
                </tr>`;

      table.appendChild(row);
    }
  }

        //   <th>#</th>
        // <th>Course Code</th>
        // <th>Course Name</th>
        // <th>Slot</th>
        // <th>Average GP</th>
        // <th>Remark</th>