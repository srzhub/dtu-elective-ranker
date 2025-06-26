//SEM 5 script

let subjectData = []; //this will hold all the data

fetch('sem3_data.json')
.then( response =>{
    if(!response.ok){
        throw new Error("Network response was not OK");
    }
    return response.json()
})
.then( data=> {
    subjectData = data;
    console.log("data loaded: ", subjectData);
    subjectData = subjectData.sort( (a,b) => parseFloat(b.grade) - parseFloat(a.grade))
    buildTable(subjectData);
})
.catch(error =>{
    console.error("There was a problem fetching data: " , error)
})


document.getElementById("order").addEventListener("change", function (){
  
  let val = this.value;
  var table = document.getElementById("5_sem_table");
  table.innerHTML = ''

  let sortedData = subjectData;

  if( val === "dec"){
  sortedData = sortedData.sort( (a,b) => parseFloat(b.grade) - parseFloat(a.grade))
 
}
else if( val === "asc"){
  sortedData = sortedData.sort( (a,b) => parseFloat(a.grade) - parseFloat(b.grade))
}

buildTable(sortedData)
})

  function buildTable(data){
    var table = document.getElementById("5_sem_table");

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