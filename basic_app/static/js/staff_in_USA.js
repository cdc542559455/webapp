function addRow() {
    var parent = document.getElementById("mytbody");
    var row = parent.childElementCount;
    var nameRIght = 2*row - 12;
    var nameLeft = nameRIght - 1;
    var newRow = document.createElement("TR");
    var newTH = document.createElement("TH");
    var newTH2 = document.createElement("TH");
    var newInput = document.createElement("INPUT");
    var newInput2 = document.createElement("INPUT");
    newInput.setAttribute("name",nameLeft);
    newInput2.setAttribute("name", nameRIght);
    newTH.appendChild(newInput);
    newTH2.appendChild(newInput2);
    newRow.appendChild(newTH);
    newRow.appendChild(newTH2);
    parent.appendChild(newRow);
}

function addDetail(){
    alert("hello");
    var parent = document.getElementById("detailbody");
    var row = parent.childElementCount;
    var newRow = document.createElement("TR");
    var newTH1 = document.createElement("TH");
    var newTH2 = document.createElement("TH");
    var newTH3 = document.createElement("TH");
    var newInput1 = document.createElement("INPUT");
    var newInput2 = document.createElement("INPUT");
    var newInput3 = document.createElement("INPUT");
    newInput1.setAttribute("type","number")
    newInput1.setAttribute("step","any")
    newInput1.setAttribute("name",(row-1)*3+11);
    newInput2.setAttribute("name",(row-1)*3+12);
    newInput3.setAttribute("name",(row-1)*3+13);
    newInput3.setAttribute("type", 'number')
    newInput3.setAttribute("step","any")
    newTH1.appendChild(newInput1);
    newTH2.appendChild(newInput2);
    newTH3.appendChild(newInput3);
    newRow.appendChild(newTH1);
    newRow.appendChild(newTH2);
    newRow.appendChild(newTH3);
    parent.appendChild(newRow);
}