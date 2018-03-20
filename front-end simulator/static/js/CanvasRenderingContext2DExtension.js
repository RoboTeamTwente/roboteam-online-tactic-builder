/**
 * Extension for the CanvasRenderingContext2D class.
 *
 * Adds functions for drawing certain types of shapes.
 */

let crc2d = CanvasRenderingContext2D.prototype;

/**
 * Starts a new path and strokes it
 *
 * @param f function (no arguments) that draws the path
 */
crc2d.strokePath = function (f) {
  this.beginPath();
  f();
  this.stroke();
};

/**
 * Draws a line from (x1, y1) to (x2, y2)
 *
 * @param x1 X-coordinate of starting point
 * @param y1 Y-coordinate of starting point
 * @param x2 X-coordinate of end point
 * @param y2 Y-coordinate of end point
 */
crc2d.strokeLine = function (x1, y1, x2, y2) {
  this.strokePath(() => {
    this.moveTo(x1, y1);
    this.lineTo(x2, y2);
  });
};

/**
 * Draws a rectangle with the strokes (lines) on the inside
 *
 * @param x X-coordinate of rectangle (including line)
 * @param y Y-coordinate of rectangle (including line)
 * @param w Width of the rectangle (including line)
 * @param h Height of the rectangle (including line)
 */
crc2d.innerStrokeRect = function (x, y, w, h) {
  let hlw = this.lineWidth / 2;

  x += hlw;
  y += hlw;

  if (w > 0) w -= this.lineWidth;
  else w += this.lineWidth;
  if (h > 0) h -= this.lineWidth;
  else h += this.lineWidth;

  this.strokeRect(x, y, w, h);
};

/**
 * Draws a rectangle with the strokes on the outside
 *
 * @param x X-coordinate of rectangle (excluding line)
 * @param y Y-coordinate of rectangle (excluding line)
 * @param w Width of the rectangle (excluding line)
 * @param h Height of the rectangle (excluding line)
 */
crc2d.outerStrokeRect = function (x, y, w, h) {
  let hlw = this.lineWidth / 2;

  x -= hlw;
  y -= hlw;

  if (w > 0) w += this.lineWidth;
  else w -= this.lineWidth;
  if (h > 0) h += this.lineWidth;
  else h -= this.lineWidth;

  this.strokeRect(x, y, w, h);
};

/**
 * Draws an arc with an inside stroke (line)
 *
 * @param x X-coordinate of arc center
 * @param y Y-coordinate of arc center
 * @param r Radius (including line)
 * @param sAngle Starting angle
 * @param eAngle End angle
 * @param counterclockwise Draw counter clockwise (optional, default: false)
 */
crc2d.innerStrokeArc = function (x, y, r, sAngle, eAngle, counterclockwise) {
  this.arc(x, y, r - this.lineWidth / 2, sAngle, eAngle, counterclockwise);
};
