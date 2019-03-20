"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var utils_1 = require("./utils");
// algorithm adapted from http://stackoverflow.com/a/14429749/3406693
function _cbb(x0, y0, x1, y1, x2, y2, x3, y3) {
    var tvalues = [];
    var bounds = [[], []];
    for (var i = 0; i <= 2; i++) {
        var a = void 0, b = void 0, c = void 0;
        if (i === 0) {
            b = ((6 * x0) - (12 * x1)) + (6 * x2);
            a = (((-3 * x0) + (9 * x1)) - (9 * x2)) + (3 * x3);
            c = (3 * x1) - (3 * x0);
        }
        else {
            b = ((6 * y0) - (12 * y1)) + (6 * y2);
            a = (((-3 * y0) + (9 * y1)) - (9 * y2)) + (3 * y3);
            c = (3 * y1) - (3 * y0);
        }
        if (Math.abs(a) < 1e-12) { // Numerical robustness
            if (Math.abs(b) < 1e-12) // Numerical robustness
                continue;
            var t = -c / b;
            if (0 < t && t < 1)
                tvalues.push(t);
            continue;
        }
        var b2ac = (b * b) - (4 * c * a);
        var sqrtb2ac = Math.sqrt(b2ac);
        if (b2ac < 0)
            continue;
        var t1 = (-b + sqrtb2ac) / (2 * a);
        if (0 < t1 && t1 < 1)
            tvalues.push(t1);
        var t2 = (-b - sqrtb2ac) / (2 * a);
        if (0 < t2 && t2 < 1)
            tvalues.push(t2);
    }
    var j = tvalues.length;
    var jlen = j;
    while (j--) {
        var t = tvalues[j];
        var mt = 1 - t;
        var x = (mt * mt * mt * x0) + (3 * mt * mt * t * x1) + (3 * mt * t * t * x2) + (t * t * t * x3);
        bounds[0][j] = x;
        var y = (mt * mt * mt * y0) + (3 * mt * mt * t * y1) + (3 * mt * t * t * y2) + (t * t * t * y3);
        bounds[1][j] = y;
    }
    bounds[0][jlen] = x0;
    bounds[1][jlen] = y0;
    bounds[0][jlen + 1] = x3;
    bounds[1][jlen + 1] = y3;
    return [
        Math.min.apply(Math, bounds[0]),
        Math.max.apply(Math, bounds[1]),
        Math.max.apply(Math, bounds[0]),
        Math.min.apply(Math, bounds[1]),
    ];
}
var BezierView = /** @class */ (function (_super) {
    tslib_1.__extends(BezierView, _super);
    function BezierView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BezierView.prototype._index_data = function () {
        var points = [];
        for (var i = 0, end = this._x0.length; i < end; i++) {
            if (isNaN(this._x0[i] + this._x1[i] + this._y0[i] + this._y1[i] + this._cx0[i] + this._cy0[i] + this._cx1[i] + this._cy1[i]))
                continue;
            var _a = _cbb(this._x0[i], this._y0[i], this._x1[i], this._y1[i], this._cx0[i], this._cy0[i], this._cx1[i], this._cy1[i]), x0 = _a[0], y0 = _a[1], x1 = _a[2], y1 = _a[3];
            points.push({ minX: x0, minY: y0, maxX: x1, maxY: y1, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    BezierView.prototype._render = function (ctx, indices, _a) {
        var sx0 = _a.sx0, sy0 = _a.sy0, sx1 = _a.sx1, sy1 = _a.sy1, scx0 = _a.scx0, scy0 = _a.scy0, scx1 = _a.scx1, scy1 = _a.scy1;
        if (this.visuals.line.doit) {
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (isNaN(sx0[i] + sy0[i] + sx1[i] + sy1[i] + scx0[i] + scy0[i] + scx1[i] + scy1[i]))
                    continue;
                ctx.beginPath();
                ctx.moveTo(sx0[i], sy0[i]);
                ctx.bezierCurveTo(scx0[i], scy0[i], scx1[i], scy1[i], sx1[i], sy1[i]);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    BezierView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    BezierView.prototype.scenterx = function () {
        throw new Error("not implemented");
    };
    BezierView.prototype.scentery = function () {
        throw new Error("not implemented");
    };
    return BezierView;
}(glyph_1.GlyphView));
exports.BezierView = BezierView;
var Bezier = /** @class */ (function (_super) {
    tslib_1.__extends(Bezier, _super);
    function Bezier(attrs) {
        return _super.call(this, attrs) || this;
    }
    Bezier.initClass = function () {
        this.prototype.type = 'Bezier';
        this.prototype.default_view = BezierView;
        this.coords([['x0', 'y0'], ['x1', 'y1'], ['cx0', 'cy0'], ['cx1', 'cy1']]);
        this.mixins(['line']);
    };
    return Bezier;
}(glyph_1.Glyph));
exports.Bezier = Bezier;
Bezier.initClass();
