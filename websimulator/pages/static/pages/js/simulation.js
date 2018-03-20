/*
JS for running simulations
Create a websocket and send the JSON tree to the back end

Created for the RoboTeam Twente as part of the Design Project for the Bachelor
Technical Computer Science of the University of Twente.

All Rights Reserved.
*/

var queue = [];

function runSimulation() {
  var editor = document.getElementById("b3js-editor").contentWindow.app.view;
  var myJSON = {
    "action": "SIM",
    "values": {"tree": JSON.parse(editor.exportToJSON())}
  };

  var ws = new WebSocket("ws://localhost:8000/");
  ws.onmessage = function (evt) {
    data = JSON.parse(evt.data);
    for(i = 0; i < data.body.simulator_output.length; i++){
      queue.push(data.body.simulator_output[i])
    }
  };
  ws.onclose = function (event) {
    console.log(event)
  };
  ws.onopen = function () {
    ws.send(JSON.stringify(myJSON));
  };
}
