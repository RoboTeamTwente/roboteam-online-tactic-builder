class Field {
  constructor(canvas) {
    this._canvas = canvas;
    this._properties = Field.DEFAULT_PROPERTIES;
    this._robots = []
  }

  static get DEFAULT_PROPERTIES() {
    return {
      background: "#006400",
      field: {
        goals: {
          lineWidth: 20,
          width: 1000,
          depth: 200,
          strokeStyle: "black"
        },
        fillStyle: "#228B22",
        lines: {
          centerCircle: {
            radius: 500
          },
          defenceArea: {
            radius: 1000,
            length: 500
          },
          support: {
            distance: 1500,
            length: 200
          },
          strokeStyle: "white",
          width: 10
        },
        size: {
          touch: 9000,
          goal: 6000
        }
      },
      box: {
        width: 250,
        strokeStyle: "black",
        lineWidth: 20,
        fillStyle: "#228B22",
      },
      outerArea: {
        width: 455,
        fillStyle: "#006400"
      },
      boxSize: function () {
        let size = this.field.size;
        let width = this.box.width;
        let goalDepth = this.field.goals.depth;
        return {
          goal: size.goal + width * 2 + goalDepth * 2,
          touch: size.touch + width * 2 + goalDepth * 2
        }
      },
      outerAreaSize: function () {
        let boxSize = this.boxSize();
        return {
          goal: boxSize.goal + this.outerArea.width * 2,
          touch: boxSize.touch + this.outerArea.width * 2
        }
      }
    }
  }

  static get ROBOT_PROPERTIES() {
    return {
      teamFillStyles: ["blue", "red"],
      radius: 100,
      cutoff: 60,
      font: "bold 120px Arial",
      textAlign: "center",
      textBaseline: "middle",
      fontFillStyle: "white",
      sAngle: function () {
        return 0 - Math.asin(this.cutoff / this.radius);
      },
      eAngle: function () {
        return Math.PI + Math.asin(this.cutoff / this.radius);
      }
    }
  }

  static get BALL_PROPERTIES() {
    return {
      diameter: 43,
      fillStyle: "orange",
      radius: function () {
        return this.diameter / 2;
      }
    }
  }

  /**
   * Returns the properties
   *
   * @returns {*} The properties
   */
  get properties() {
    return this._properties;
  }

  /**
   * Returns the corresponding Canvas
   *
   * @returns {jQuery}
   */
  get canvas() {
    return this._canvas;
  }

  /**
   * Gets the robot data
   * @returns {*}
   */
  get robots() {
    return this._robots;
  }

  get ball() {
    return this._ball;
  }

  set components(value) {
    this._ball = value.ball;
    this._robots = value.robots;
  }

  /**
   * Calculates the drawing parameters (orientation and scale)
   *
   * @returns {{landscape: boolean, scale: number}} Drawing parameters
   */
  getDrawParameters() {
    let outer_size = this.properties.outerAreaSize();
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

  /**
   * Transforms the canvas according to the drawing parameters
   */
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

  /**
   * Draws the outer (referee) area
   */
  drawOuterArea() {
    let dim = this.properties.outerAreaSize();
    let fillStyle = this.properties.outerArea.fillStyle;

    this.canvas.edit((ctx) => {
      ctx.fillStyle = fillStyle;
      ctx.fillRect(-dim.goal / 2, -dim.touch / 2, dim.goal, dim.touch);
    });
  }

  /**
   * Draws the box around the field
   */
  drawBox() {
    let box = this.properties.box;
    let dim = this.properties.boxSize();

    this.canvas.edit((ctx) => {
      // Apply styles
      ctx.lineWidth = box.lineWidth;
      ctx.strokeStyle = box.strokeStyle;
      ctx.fillStyle = box.fillStyle;

      // Draw box
      let x = -dim.goal / 2;
      let y = -dim.touch / 2;
      ctx.fillRect(x, y, dim.goal, dim.touch);
      ctx.outerStrokeRect(x, y, dim.goal, dim.touch);
    });
  }

  /**
   * Draws the field and it's lines
   */
  drawField() {
    let field = this.properties.field;

    this.canvas.edit((ctx) => {
      // Apply styles
      ctx.lineWidth = field.lines.width;
      ctx.strokeStyle = field.lines.strokeStyle;
      ctx.fillStyle = field.fillStyle;

      // Init variables
      let dim, x, y, r;

      // Draw field background and outer lines
      dim = field.size;
      x = -dim.goal / 2;
      y = -dim.touch / 2;
      ctx.fillRect(x, y, dim.goal, dim.touch);
      ctx.innerStrokeRect(x, y, dim.goal, dim.touch);

      // Draw center lines and circle
      ctx.strokeLine(x, 0, -x, 0);
      ctx.strokeLine(0, y, 0, -y);
      ctx.strokePath(() => ctx.innerStrokeArc(0, 0, field.lines.centerCircle.radius, 0, 2 * Math.PI));

      // Draw support lines
      x = field.lines.support.length / 2;
      y = field.lines.support.distance;
      ctx.strokeLine(-x, -y, x, -y);
      ctx.strokeLine(-x, y, x, y);

      // Draw defence areas
      x = field.lines.defenceArea.length / 2;
      y = field.size.touch / 2;
      r = field.lines.defenceArea.radius;
      ctx.strokePath(() => {
        ctx.innerStrokeArc(x, -y, r, 0, 0.5 * Math.PI);
        ctx.innerStrokeArc(-x, -y, r, 0.5 * Math.PI, Math.PI);
      });
      ctx.strokePath(() => {
        ctx.innerStrokeArc(-x, y, r, Math.PI, 1.5 * Math.PI);
        ctx.innerStrokeArc(x, y, r, Math.PI * 1.5, Math.PI * 2);
      });
    });
  }

  /**
   * Draws the goals of the field
   */
  drawGoals() {
    let field = this.properties.field;
    let goals = field.goals;

    this.canvas.edit((ctx) => {
      // Apply styles
      ctx.strokeStyle = goals.strokeStyle;
      ctx.lineWidth = goals.lineWidth;

      // Calculate parameters
      let x = goals.width / 2;
      let y1 = field.size.touch / 2;
      let y2 = y1 + goals.depth;

      // Draw two goals
      ctx.strokePath(() => {
        ctx.moveTo(-x, -y1);
        ctx.lineTo(-x, -y2);
        ctx.lineTo(x, -y2);
        ctx.lineTo(x, -y1);
      });
      ctx.strokePath(() => {
        ctx.moveTo(-x, y1);
        ctx.lineTo(-x, y2);
        ctx.lineTo(x, y2);
        ctx.lineTo(x, y1);
      });
    });
  }

  drawRobots() {
    this.canvas.edit((ctx) => {
      let p = Field.ROBOT_PROPERTIES;

      // Draw all robots
      for (let r of this.robots) {
        // Save current transformation
        ctx.save();

        // Make new transformation
        ctx.translate(-r.y, -r.x);
        ctx.rotate(-r.orientation);

        // Set fillStyle and draw robot
        ctx.fillStyle = p.teamFillStyles[r.team];

        ctx.beginPath();
        ctx.arc(0, 0, p.radius, p.sAngle(), p.eAngle());
        ctx.fill();

        // Set font properties
        ctx.font = p.font;
        ctx.textAlign = p.textAlign;
        ctx.textBaseline = p.textBaseline;
        ctx.fillStyle = p.fontFillStyle;

        // Add ID to robot
        ctx.fillText(r.id, 0, (p.radius - p.cutoff) / 2);

        // Restore old transformation
        ctx.restore();
      }
    })
  }

  drawBall() {
    let b = this.ball;
    if (b === undefined || b === null) return;

    let p = Field.BALL_PROPERTIES;

    this.canvas.edit((ctx) => {
      ctx.fillStyle = p.fillStyle;

      ctx.beginPath();
      ctx.arc(-b.y, -b.x, p.radius(), 0, Math.PI * 2);
      ctx.fill();
    })
  }

  /**
   * Draws a the field
   */
  draw() {
    // Resize, clear and transform canvas
    this.canvas.resizeToContainer();
    this.canvas.clear();
    this.transformCanvas();

    // Set background
    this.canvas.jQuery.css("background", this.properties.background);

    // Draw field components
    this.drawOuterArea();
    this.drawBox();
    this.drawField();
    this.drawGoals();

    // Draw robots and ball
    this.drawRobots();
    this.drawBall();
  }
}
