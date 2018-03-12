class Field {
  constructor(canvas) {
    this._canvas = canvas;
    this._properties = Field.DEFAULT_PROPERTIES;
  }

  static get DEFAULT_PROPERTIES() {
    return {
      touch_boundary_length: 9000,
      goal_boundary_length: 6000,
      center_circle_diameter: 1000,
      line_width: 10,
      defence_area: {
        circle_radius: 1000,
        line_length: 500,
      },
      goal: {
        post_width: 20,
        width: 1000,
        height: 180
      },
      padding: 300,
      margin: 100,
      color: "green",
      field_size: function () {
        return {
          touch: this.touch_boundary_length,
          goal: this.goal_boundary_length
        }
      },
      box_size: function () {
        let padding = this.padding * 2;
        return {
          touch: this.field_size().touch + padding,
          goal: this.field_size().goal + padding
        }
      },
      outer_size: function () {
        let margin = this.margin * 2;
        return {
          touch: this.box_size().touch + margin,
          goal: this.box_size().goal + margin
        }
      },
    };
  }

  get properties() {
    return this._properties;
  }

  get size() {
    return {
      touch_boundary: this.properties.touch_boundary_length + this.properties.margin * 2,
      goal_boundary: this.properties.goal_boundary_length + this.properties.margin * 2
    }
  }

  get canvas() {
    return this._canvas;
  }

  getDrawParameters() {
    let outer_size = this.properties.outer_size();
    let t = outer_size.touch;
    let g = outer_size.goal;
    let w = canvas.width;
    let h = canvas.height;

    // Calculate scale factors for horizontal and vertical
    let hor_scale = Math.min(w / t, h / g);
    let ver_scale = Math.min(w / g, h / t);

    // Get orientation
    let hor = hor_scale > ver_scale;

    return {
      landscape: hor,
      scale: hor ? hor_scale : ver_scale
    }
  }

  transformCanvas() {
    this.canvas.edit((ctx) => {
      // Reset current transformation
      ctx.transform(1, 0, 0, 1, 0, 0);

      // Set position to canvas center
      ctx.translate(this.canvas.width / 2, this.canvas.height / 2);

      // Get draw parameters
      let params = this.getDrawParameters();

      // Rotate and scale canvas
      if (params.landscape) ctx.rotate(Math.PI / 2);
      ctx.scale(params.scale, params.scale);
    })
  }

  draw() {
    this.canvas.clear();

    // Set defaults
    Line.defaultWidth = 10;
    Line.defaultStrokeStyle = "white";

    this.canvas.resizeToContainer();
    this.canvas.clear();
    this.transformCanvas();
    this.canvas.edit((ctx) => {
      var size = this.properties.box_size();

      // Draw outer box
      ctx.lineWidth = 20;
      ctx.strokeRect(-(size.goal / 2 + ctx.lineWidth), -(size.touch / 2 + ctx.lineWidth), size.goal + ctx.lineWidth, size.touch + ctx.lineWidth);

      // Draw inner box
      ctx.lineWidth = 10;
      ctx.strokeStyle = "white";
      size = this.properties.field_size();
      ctx.strokeRect(-(size.goal / 2 - ctx.lineWidth), -(size.touch / 2 - ctx.lineWidth), size.goal - ctx.lineWidth, size.touch - ctx.lineWidth);

      // Draw center line
      ctx.beginPath();
      ctx.moveTo(-(size.goal - ctx.lineWidth) / 2, 0);
      ctx.lineTo((size.goal - ctx.lineWidth) / 2, 0);
      ctx.stroke();

      // Draw center circle
      ctx.beginPath();
      ctx.arc(0, 0, this.properties.center_circle_diameter / 2 - ctx.lineWidth, 0, Math.PI * 2);
      ctx.stroke();

      // Draw long center line
      ctx.beginPath();
      ctx.moveTo(0, -(size.touch - ctx.lineWidth) / 2);
      ctx.lineTo(0, (size.touch - ctx.lineWidth) / 2);
      ctx.stroke();

      // Draw defending areas lines
      var def = this.properties.defence_area;
      ctx.beginPath();
      ctx.arc(-(def.line_length / 2), -(size.touch) / 2, def.circle_radius - ctx.lineWidth / 2, Math.PI / 2, Math.PI, false);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(-(def.line_length) / 2, -(size.touch / 2 - def.circle_radius + ctx.lineWidth / 2));
      ctx.lineTo((def.line_length) / 2, -(size.touch / 2 - def.circle_radius + ctx.lineWidth / 2));
      ctx.stroke();
      ctx.beginPath();
      ctx.arc((def.line_length / 2), -(size.touch) / 2, def.circle_radius - ctx.lineWidth / 2, 0, Math.PI / 2);
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(-(def.line_length / 2), (size.touch) / 2, def.circle_radius - ctx.lineWidth / 2, -Math.PI, -Math.PI / 2, false);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(-(def.line_length) / 2, (size.touch / 2 - def.circle_radius + ctx.lineWidth / 2));
      ctx.lineTo((def.line_length) / 2, (size.touch / 2 - def.circle_radius + ctx.lineWidth / 2));
      ctx.stroke();
      ctx.beginPath();
      ctx.arc((def.line_length / 2), (size.touch) / 2, def.circle_radius - ctx.lineWidth / 2, -Math.PI / 2, 0);
      ctx.stroke();
    });

    // // Draw the field
    // this.canvas.edit((ctx, canvas) => {
    //   console.log("Drawing outer box");
    //   // Draw box
    //   var box_size = this.properties.box_size();
    //   var l = Line.defaultWidth;
    //   var x = box_size.touch/2 + l;
    //   var y = box_size.goal/2 + l;
    //   ctx.strokeStyle = "black";
    //   ctx.fillRect(-x, y, box_size.touch + l, box_size.goal + 1);
    // })
  }
}