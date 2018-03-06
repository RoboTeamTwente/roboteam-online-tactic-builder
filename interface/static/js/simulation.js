function runSimulation() {
  var editor = document.getElementById("b3js-editor").contentWindow.app.view;

  var w = window.open("", "Code");
  w.document.write(editor.exportToJSON());
}
