"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var utils_1 = require("./utils");
// Formula from: http://pomax.nihongoresources.com/pages/bezier/
//
// if segment is quadratic bezier do:
//   for both directions do:
//     if control between start and end, compute linear bounding box
//     otherwise, compute
//       bound = u(1-t)^2 + 2v(1-t)t + wt^2
//         (with t = ((u-v) / (u-2v+w)), with {u = start, v = control, w = end})
//       if control precedes start, min = bound, otherwise max = bound
function _qbb(u, v, w) {
    if (v == (u + w) / 2)
        return [u, w];
    else {
        var t = (u - v) / ((u - (2 * v)) + w);
        var bd = (u * Math.pow((1 - t), 2)) + (2 * v * (1 - t) * t) + (w * Math.pow(t, 2));
        return [Math.min(u, w, bd), Math.max(u, w, bd)];
    }
}
var QuadraticView = /** @class */ (function (_super) {
    tslib_1.__extends(QuadraticView, _super);
    function QuadraticView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    QuadraticView.prototype._index_data = function () {
        var points = [];
        for (var i = 0, end = this._x0.length; i < end; i++) {
            if (isNaN(this._x0[i] + this._x1[i] + this._y0[i] + this._y1[i] + this._cx[i] + this._cy[i]))
                continue;
            var _a = _qbb(this._x0[i], this._cx[i], this._x1[i]), x0 = _a[0], x1 = _a[1];
            var _b = _qbb(this._y0[i], this._cy[i], this._y1[i]), y0 = _b[0], y1 = _b[1];
            points.push({ minX: x0, minY: y0, maxX: x1, maxY: y1, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    QuadraticView.prototype._render = function (ctx, indices, _a) {
        var sx0 = _a.sx0, sy0 = _a.sy0, sx1 = _a.sx1, sy1 = _a.sy1, scx = _a.scx, scy = _a.scy;
        if (this.visuals.line.doit) {
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (isNaN(sx0[i] + sy0[i] + sx1[i] + sy1[i] + scx[i] + scy[i]))
                    continue;
                ctx.beginPath();
                ctx.moveTo(sx0[i], sy0[i]);
                ctx.quadraticCurveTo(scx[i], scy[i], sx1[i], sy1[i]);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    QuadraticView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    QuadraticView.prototype.scenterx = function () {
        throw new Error("not implemented");
    };
    QuadraticView.prototype.scentery = function () {
        throw new Error("not implemented");
    };
    return QuadraticView;
}(glyph_1.GlyphView));
exports.QuadraticView = QuadraticView;
var Quadratic = /** @class */ (function (_super) {
    tslib_1.__extends(Quadratic, _super);
    function Quadratic(attrs) {
        return _super.call(this, attrs) || this;
    }
    Quadratic.initClass = function () {
        this.prototype.type = 'Quadratic';
        this.prototype.default_view = QuadraticView;
        this.coords([['x0', 'y0'], ['x1', 'y1'], ['cx', 'cy']]);
        this.mixins(['line']);
    };
    return Quadratic;
}(glyph_1.Glyph));
exports.Quadratic = Quadratic;
Quadratic.initClass();
