/*
JS for running simulations

Created for the RoboTeam Twente as part of the Design Project for the Bachelor
Technical Computer Science of the University of Twente.

All Rights Reserved.
*/

function runSimulation() {
  var editor = document.getElementById("b3js-editor").contentWindow.app.view;

  var w = window.open("", "Code");
  w.document.write(editor.exportToJSON());

  // TODO LATER Make sure it properly communicates with the simulator
}
