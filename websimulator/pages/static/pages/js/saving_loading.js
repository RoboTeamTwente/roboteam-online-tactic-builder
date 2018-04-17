/*
  Functions in order to properly save or load a tree
*/


/*
Verify whether a method requires CSRF protection
 */
function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
Saves the tree that is currently visible on the screen
Sends an AJAX request with the tree to the API backend
 */
function saveTree(csrf_token, name) {
  var editor = document.getElementById("b3js-editor").contentWindow.app.view;
  var myJSON = JSON.parse(editor.exportToJSON());

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
      }
    }
  });

  $.ajax({
    type: "POST",
    url: "/tree/",
    csrfmiddlewaretoken: csrf_token,
    data: JSON.stringify({"tree": JSON.stringify(myJSON), "name": name}),
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    success: function (response) {
      if (parseInt(response, 10) !== 200) {
        $.notify({
          message: 'Invalid name or user'
        }, {
          type: 'warning',
          placement: {
            from: 'bottom'
          }
        });
      }
      else {
        $.notify({
          message: 'Tree saved!'
        }, {
          type: 'success',
          placement: {
            from: 'bottom'
          }
        });
      }
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      $.notify({
        message: 'Something went wrong...'
      }, {
        type: 'danger',
        placement: {
          from: 'bottom'
        }
      });
     }
  });
}

// Load all trees in the dialog
// First obtain all the trees belonging to the logged in account
// Then create an HTML list with radio buttons and insert it in the placeholder list
function showTrees(csrf_token) {
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
      }
    }
  });
  var output = null;
  $.ajax({
    type: "GET",
    async: false,
    url: "/available_trees/",
    data: {},
    csrfmiddlewaretoken: csrf_token,
    success: function (data) {
      if (parseInt(data, 10) === 404) {
        $.notify({
          // options
          message: 'No trees belonging to this account'
        }, {
          // settings
          type: 'warning',
          placement: {
            from: 'bottom'
          }
        });
      } else {
        output = data["data"];

        let ul = document.getElementById("treeList");
        while (ul.firstChild) {
          ul.removeChild(ul.firstChild);
        }

        for (let i = 0; i < output.length; i++) {
          let li = document.createElement('li');
          let input = document.createElement('input');
          let label = document.createElement('label');
          let text = document.createTextNode(output[i]);

          input.setAttribute("type", "radio");
          input.setAttribute("value", output[i]);
          input.setAttribute("name", "radio_tree");

          label.setAttribute("style", "color:white");

          label.appendChild(input);
          label.appendChild(text);
          li.appendChild(label);
          ul.appendChild(li);
        }
      }
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      $.notify({
        message: 'Something went wrong...'
      }, {
        type: 'danger',
        placement: {
          from: 'bottom'
        }
      });
    }
  });

}


/*
Gets the tree from the database with the corresponding name
 */
function getTree(csrf_token, name) {
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
      }
    }
  });
  var output = null;
  $.ajax({
    type: "GET",
    async: false,
    url: "/tree/",
    csrfmiddlewaretoken: csrf_token,
    data: {
      name: name
    },
    success: function (data) {
      output = data;
      $.notify({
        // options
        message: 'Tree loaded!'
      }, {
        // settings
        type: 'success',
        placement: {
          from: 'bottom'
        }
      });
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      $.notify({
        message: 'Something went wrong...'
      }, {
        type: 'danger',
        placement: {
          from: 'bottom'
        }
      });
    }
  });
  return output;
}

/*
Function loading a new tree from JSON into the editor
First removes all the current blocks
Then adds new ones and forms the connections
Based on the importToJSON function
 */
function loadTree(json_tree) {
  var editor = document.getElementById("b3js-editor").contentWindow.app.view;

  blocks = [];

  for (i = 0; i < editor.blocks.length; i++) {
    blocks.push(editor.blocks[i]);
  }

  for (i = 1; i < blocks.length; i++) {
    editor.removeBlock(blocks[i]);
  }

  c = null;

  for (var node in json_tree.nodes) {
    var json_node = json_tree.nodes[node],
        new_node = editor.addBlock(
            json_node.name,
            json_node.display.x,
            json_node.display.y
        );
    new_node.id = json_node.id,
        new_node.title = json_node.title,
        new_node.description = json_node.description,
        new_node.parameters = json_node.parameters,
        new_node.properties = json_node.properties,
        new_node.redraw(),
    new_node.id === json_tree.root && (c = new_node)
  }

  for (var node in json_tree.nodes) {
    var json_node = json_tree.nodes[node],
        current_node = editor.getBlockById(node),
        children = null;
    if ("composite" == current_node.category && json_node.children ? children = json_node.children : ("decorator" == current_node.category && json_node.child || "root" == current_node.category && json_node.child) && (children = [json_node.child]), children)
      for (var i = 0; i < children.length; i++) {
        var j = editor.getBlockById(children[i]);
        editor.addConnection(current_node, j)
      }
  }
  c && editor.addConnection(editor.getRoot(), c), editor.ui.camera.x = json_tree.display.camera_x, editor.ui.camera.y = json_tree.display.camera_y, editor.ui.camera.scaleX = json_tree.display.camera_z, editor.ui.camera.scaleY = json_tree.display.camera_z;

  editor.organize();
}