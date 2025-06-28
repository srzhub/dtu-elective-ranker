//SEM 5 script

let subjectData = []; //this will hold all the data

fetch('../json_data/sem7_data.json')
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

// Function to change table, either sort or filter or both.
function changeTable(){
  var table = document.getElementById("7_sem_table");
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

  buildTable(changedData)
}

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

  function buildTable(data){
    var table = document.getElementById("7_sem_table");

    for(var i = 0; i< data.length; i++ ){
      const row = 
        `<tr>
                  <td>${i+1}</td>
                  <td>${data[i].code}</td>
                  <td>${data[i].title}</td>
                  <td>${data[i].grade}</td>
                </tr>`

      table.innerHTML += row;
    }
  }