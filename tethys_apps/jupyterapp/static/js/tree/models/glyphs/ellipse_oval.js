"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var center_rotatable_1 = require("./center_rotatable");
var hittest = require("core/hittest");
var EllipseOvalView = /** @class */ (function (_super) {
    tslib_1.__extends(EllipseOvalView, _super);
    function EllipseOvalView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    EllipseOvalView.prototype._set_data = function () {
        this.max_w2 = 0;
        if (this.model.properties.width.units == "data")
            this.max_w2 = this.max_width / 2;
        this.max_h2 = 0;
        if (this.model.properties.height.units == "data")
            this.max_h2 = this.max_height / 2;
    };
    EllipseOvalView.prototype._map_data = function () {
        if (this.model.properties.width.units == "data")
            this.sw = this.sdist(this.renderer.xscale, this._x, this._width, 'center');
        else
            this.sw = this._width;
        if (this.model.properties.height.units == "data")
            this.sh = this.sdist(this.renderer.yscale, this._y, this._height, 'center');
        else
            this.sh = this._height;
    };
    EllipseOvalView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sw = _a.sw, sh = _a.sh, _angle = _a._angle;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + sw[i] + sh[i] + _angle[i]))
                continue;
            ctx.beginPath();
            ctx.ellipse(sx[i], sy[i], sw[i] / 2.0, sh[i] / 2.0, _angle[i], 0, 2 * Math.PI);
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                ctx.fill();
            }
            if (this.visuals.line.doit) {
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    EllipseOvalView.prototype._hit_point = function (geometry) {
        var _a, _b, _c, _d;
        var x0, x1, y0, y1, cond, dist, sx0, sx1, sy0, sy1;
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        if (this.model.properties.width.units == "data") {
            x0 = x - this.max_width;
            x1 = x + this.max_width;
        }
        else {
            sx0 = sx - this.max_width;
            sx1 = sx + this.max_width;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        }
        if (this.model.properties.height.units == "data") {
            y0 = y - this.max_height;
            y1 = y + this.max_height;
        }
        else {
            sy0 = sy - this.max_height;
            sy1 = sy + this.max_height;
            _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        }
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var candidates = this.index.indices(bbox);
        var hits = [];
        for (var _i = 0, candidates_1 = candidates; _i < candidates_1.length; _i++) {
            var i = candidates_1[_i];
            cond = hittest.point_in_ellipse(sx, sy, this._angle[i], this.sh[i] / 2, this.sw[i] / 2, this.sx[i], this.sy[i]);
            if (cond) {
                ;
                _c = this.renderer.xscale.r_compute(x, this._x[i]), sx0 = _c[0], sx1 = _c[1];
                _d = this.renderer.yscale.r_compute(y, this._y[i]), sy0 = _d[0], sy1 = _d[1];
                dist = Math.pow(sx0 - sx1, 2) + Math.pow(sy0 - sy1, 2);
                hits.push([i, dist]);
            }
        }
        return hittest.create_hit_test_result_from_hits(hits);
    };
    EllipseOvalView.prototype.draw_legend_for_index = function (ctx, _a, index) {
        var x0 = _a.x0, y0 = _a.y0, x1 = _a.x1, y1 = _a.y1;
        var len = index + 1;
        var sx = new Array(len);
        sx[index] = (x0 + x1) / 2;
        var sy = new Array(len);
        sy[index] = (y0 + y1) / 2;
        var scale = this.sw[index] / this.sh[index];
        var d = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.8;
        var sw = new Array(len);
        var sh = new Array(len);
        if (scale > 1) {
            sw[index] = d;
            sh[index] = d / scale;
        }
        else {
            sw[index] = d * scale;
            sh[index] = d;
        }
        this._render(ctx, [index], { sx: sx, sy: sy, sw: sw, sh: sh }); // XXX
    };
    EllipseOvalView.prototype._bounds = function (_a) {
        var minX = _a.minX, maxX = _a.maxX, minY = _a.minY, maxY = _a.maxY;
        return {
            minX: minX - this.max_w2,
            maxX: maxX + this.max_w2,
            minY: minY - this.max_h2,
            maxY: maxY + this.max_h2,
        };
    };
    return EllipseOvalView;
}(center_rotatable_1.CenterRotatableView));
exports.EllipseOvalView = EllipseOvalView;
var EllipseOval = /** @class */ (function (_super) {
    tslib_1.__extends(EllipseOval, _super);
    function EllipseOval(attrs) {
        return _super.call(this, attrs) || this;
    }
    EllipseOval.initClass = function () {
        this.prototype.type = 'EllipseOval';
    };
    return EllipseOval;
}(center_rotatable_1.CenterRotatable));
exports.EllipseOval = EllipseOval;
EllipseOval.initClass();
