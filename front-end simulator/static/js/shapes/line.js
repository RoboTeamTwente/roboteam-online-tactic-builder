class Line {
  constructor(x1, y1, x2, y2, strokeStyle, lineWidth) {
    this._x1 = x1;
    this._y1 = y1;
    this._x2 = x2;
    this._y2 = y2;
    this.strokeStyle = strokeStyle;
    this.lineWidth = lineWidth;
  }

  draw(ctx) {
    ctx.beginPath();
    ctx.moveTo(this._x1, this._y1);
    ctx.lineTo(this._x2, this._y2);
    ctx.strokeStyle = this.strokeStyle !== undefined ? this.strokeStyle : ctx.strokeStyle;
    ctx.lineWidth = this.lineWidth !== undefined ? this.strokeStyle : ctx.strokeStyle;
    ctx.stroke();
  }
}