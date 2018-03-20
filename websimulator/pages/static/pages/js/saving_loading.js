/*
  Functions in order to properly save a tree
*/

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function saveTree(csrf_token) {
  var editor = document.getElementById("b3js-editor").contentWindow.app.view;
  var myJSON = JSON.parse(editor.exportToJSON());
  console.log(myJSON);
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
    data: JSON.stringify(myJSON),
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    success: function () {
      alert("Saved! It worked.");
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      alert("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
    }
  });

  // blocks = [];
  //
  // for (i = 0; i < editor.blocks.length; i++) {
  //   blocks.push(editor.blocks[i]);
  // }
  //
  // console.log(blocks);
  //
  // for (i = 1; i < blocks.length; i++){
  //   editor.removeBlock(blocks[i]);
  // }
  //
  // importFromJSON(myJSON, editor)

}

function importFromJSON(a, editor) {
  var b = a,
    c = null;
  for (var d in b.nodes) {
    var e = b.nodes[d],
      f = editor.addBlock(e.name, e.display.x, e.display.y);
    f.id = e.id,
      f.title = e.title,
      f.description = e.description,
      f.parameters = e.parameters,
      f.properties = e.properties,
      f.redraw(),
    f.id === b.root && (c = f)
  }
  for (var d in b.nodes) {
    var e = b.nodes[d],
      g = editor.getBlockById(d),
      h = null;
    if ("composite" == g.category && e.children ? h = e.children : ("decorator" == g.category && e.child || "root" == g.category && e.child) && (h = [e.child]), h)
      for (var i = 0; i < h.length; i++) {
        var j = editor.getBlockById(h[i]);
        editor.addConnection(g, j)
      }
  }
  c && editor.addConnection(editor.getRoot(), c), editor.ui.camera.x = b.display.camera_x, editor.ui.camera.y = b.display.camera_y, editor.ui.camera.scaleX = b.display.camera_z, editor.ui.camera.scaleY = b.display.camera_z
}