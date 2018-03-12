class Canvas {
  constructor(canvasId, containerId) {
    // Initialize variables
    this._canvas = $("#" + canvasId);
    this._container = $("#" + containerId);
    this._ctx = this.canvas.getContext("2d");
  }

  get jQuery() {
    return this._canvas;
  }

  get canvas() {
    return this._canvas[0];
  }

  get ctx() {
    return this._ctx;
  }

  get container() {
    return this._container;
  }

  get height() {
    return this.canvas.height;
  }

  set height(value) {
    this.canvas.height = value;
  }

  get width() {
    return this.canvas.width;
  }

  set width(value) {
    this.canvas.width = value;
  }

  clear() {
    let ctx = this._ctx;

    ctx.beginPath();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(-this.width, -this.height, 3 * this.width, 3 * this.height);
  }

  edit(f) {
    f(this._ctx, this);
  }

  resizeToContainer() {
    this.height = this.container.height();
    this.width = this.container.width();
  }
}