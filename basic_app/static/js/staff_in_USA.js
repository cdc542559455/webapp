function addRow() {
    var parent = document.getElementById("mytbody");
    var newRow = document.createElement("TR");
    var newTH = document.createElement("TH");
    var newTH2 = document.createElement("TH");
    var newInput = document.createElement("INPUT");
    var newInput2 = document.createElement("INPUT");
    newTH.appendChild(newInput);
    newTH2.appendChild(newInput2);
    newRow.appendChild(newTH);
    newRow.appendChild(newTH2);
    parent.appendChild(newRow);
}