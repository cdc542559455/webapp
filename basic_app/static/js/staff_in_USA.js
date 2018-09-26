function addRow() {
    var parent = document.getElementById("mytbody");
    var row = parent.childElementCount;
    var nameRIght = 2*row - 14;
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
    var parent = document.getElementById("detailbody");
    var newRow = document.createElement("TR");
    var newTH1 = document.createElement("TH");
    var newTH2 = document.createElement("TH");
    var newTH3 = document.createElement("TH");
    var newInput1 = document.createElement("INPUT");
    var newInput2 = document.createElement("INPUT");
    var newInput3 = document.createElement("INPUT");
    newTH1.appendChild(newInput1);
    newTH2.appendChild(newInput2);
    newTH3.appendChild(newInput3);
    newRow.appendChild(newTH1);
    newRow.appendChild(newTH2);
    newRow.appendChild(newTH3);
    parent.appendChild(newRow);
}