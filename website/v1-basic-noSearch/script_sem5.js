//SEM 5 script

let subjectData = []; //this will hold all the data

fetch('sem5_clean.json')
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