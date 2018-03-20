/**
 * Class for working with the HTML Canvas and adding some extra functionality
 */
class Canvas {
  /**
   * Constructs a canvas from an ID and it's container
   *
   * @param canvasId HTML ID of the canvas
   * @param containerId HTML ID of the container of the canvas
   */
  constructor(canvasId, containerId) {
    this._canvas = $("#" + canvasId);
    this._container = $("#" + containerId);
    this._ctx = this.canvas.getContext("2d");
  }

  /**
   * Returns the jQuery object of the canvas
   *
   * @returns {jQuery} jQuery object of the canvas
   */
  get jQuery() {
    return this._canvas;
  }

  /**
   * Returns the canvas HTML element
   * @returns {HTMLElement} the Canvas HTML element
   */
  get canvas() {
    return this._canvas[0];
  }

  /**
   * Returns the canvas 2D context
   *
   * @returns {CanvasRenderingContext2D} Canvas 2D context
   */
  get ctx() {
    return this._ctx;
  }

  /**
   * Returns the jQuery object of the container
   *
   * @returns {jQuery} jQuery object of the container
   */
  get container() {
    return this._container;
  }

  /**
   * Returns the height of the canvas
   */
  get height() {
    return this.canvas.height;
  }

  /**
   * Sets the height of the canvas
   *
   * @param value The new height
   */
  set height(value) {
    this.canvas.height = value;
  }

  /**
   * Returns the width of the canvas
   */
  get width() {
    return this.canvas.width;
  }

  /**
   * Sets the width of the canvas
   *
   * @param value The new width
   */
  set width(value) {
    this.canvas.width = value;
  }

  /**
   * Clears the canvas
   */
  clear() {
    let ctx = this._ctx;

    ctx.beginPath();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(-this.width, -this.height, 3 * this.width, 3 * this.height);
  }

  /**
   * Function to edit the canvas
   *
   * @param f function(this.ctx, this) in which the canvas is edited
   */
  edit(f) {
    f(this._ctx, this);
  }

  /**
   * Resize the canvas to it's container
   */
  resizeToContainer() {
    this.height = this.container.height();
    this.width = this.container.width();
  }
}