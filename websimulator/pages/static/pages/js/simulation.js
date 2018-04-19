/*
JS for running simulations
Create a websocket and send the JSON tree to the back end

Created for the RoboTeam Twente as part of the Design Project for the Bachelor
Technical Computer Science of the University of Twente.

All Rights Reserved.
*/

var queue = [];

var AnimationStatus = {
    READY: 1,
    SUBMITTED: 2,
    QUEUED: 3,
    GENERATING: 4,
    STARTING_SIMULATION: 5,
    SIMULATING: 6,
    BUFFERING: 7,
    FINISHED: 8,
    properties: {
        1: {
            action: function (show, hide) {
                show("Ready to start a new simulation.", "primary");
            },
        },
        2: {
            action: function (show, hide) {
                show("Submitted tree to the server.", "secondary");
            }
        },
        3: {
            action: function(show, hide) {
                show("Placed into simulation queue.", "secondary");
            }
        },
        4: {
            action: function(show, hide) {
                show("Generating the code for simulation, this will take about 30 seconds.", "warning");
            }
        },
        5: {
            action: function(show, hide) {
                show("Starting the simulation, it will start in a few seconds.", "success");
            }
        },
        6: {
            action: function(show, hide) {
                hide();
            }
        },
        7: {
            action: function(show, hide) {
                show("Buffering the simulation results.", "info");
            }
        },
        8: {
            action: function(show, hide) {
                show("The simulation has finished.", "success");
            }
        }
    }
};

var gui_status = AnimationStatus.READY;
var buffer_size = 30;

function changeGuiStatus(status, simulator) {
    gui_status = status;
    AnimationStatus.properties[gui_status].action(simulator.showOverlay, simulator.hideOverlay);
    if(status === AnimationStatus.FINISHED) {
      $("#btnRunSimulation").prop('disabled', false);
      $("#btnNavLoad").prop('disabled', false);
      $("#btnNavSave").prop('disabled', false);
      $("#btnGoogleLogin").prop('disabled', false);
      $("#btnGoogleLogout").prop('disabled', false);
    }
}

function runSimulation(assignmentId) {
    var editor = document.getElementById("b3js-editor").contentWindow.app.view;
    var myJSON = {
        "action": "SIM",
        "values": {"tree": JSON.parse(editor.exportToJSON()), "assignment_id": assignmentId}
    };

    if(myJSON['values']['tree']['root'] == null) {
        $.notify({
          message: 'Tree must contain at least one node'
        },{
          type: 'warning',
          placement: {
            from: 'bottom'
          }
        });
        changeGuiStatus(AnimationStatus.FINISHED, getSimulator());
    } else {
      showSinglePanel("#panel-simulation");
      var ws = new WebSocket("ws://" + window.location.hostname +  ":8000/");
      buffer_size = 30;
      ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if ("simulator_output" in data.body) {
          for (i = 0; i < data.body.simulator_output.length; i++) {
            queue.push(data.body.simulator_output[i])
          }
        }

        if ("simulator_status" in data.body) {
          if (data.body.simulator_status === AnimationStatus.FINISHED) {
            queue.push({
              frame_number: -1
            });
            ws.close();
            changeGuiStatus(AnimationStatus.SIMULATING, getSimulator());
          } else {
            changeGuiStatus(data.body.simulator_status, getSimulator());
          }
        }
      };
      ws.onclose = function (event) {
        console.log(event)
      };
      ws.onopen = function () {
        ws.send(JSON.stringify(myJSON));
      };
    }

}
