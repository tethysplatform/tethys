"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var hittest = require("core/hittest");
var p = require("core/properties");
var math_1 = require("core/util/math");
var AnnularWedgeView = /** @class */ (function (_super) {
    tslib_1.__extends(AnnularWedgeView, _super);
    function AnnularWedgeView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AnnularWedgeView.prototype._map_data = function () {
        if (this.model.properties.inner_radius.units == "data")
            this.sinner_radius = this.sdist(this.renderer.xscale, this._x, this._inner_radius);
        else
            this.sinner_radius = this._inner_radius;
        if (this.model.properties.outer_radius.units == "data")
            this.souter_radius = this.sdist(this.renderer.xscale, this._x, this._outer_radius);
        else
            this.souter_radius = this._outer_radius;
        this._angle = new Float32Array(this._start_angle.length);
        for (var i = 0, end = this._start_angle.length; i < end; i++) {
            this._angle[i] = this._end_angle[i] - this._start_angle[i];
        }
    };
    AnnularWedgeView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, _start_angle = _a._start_angle, _angle = _a._angle, sinner_radius = _a.sinner_radius, souter_radius = _a.souter_radius;
        var direction = this.model.properties.direction.value();
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + sinner_radius[i] + souter_radius[i] + _start_angle[i] + _angle[i]))
                continue;
            ctx.translate(sx[i], sy[i]);
            ctx.rotate(_start_angle[i]);
            ctx.moveTo(souter_radius[i], 0);
            ctx.beginPath();
            ctx.arc(0, 0, souter_radius[i], 0, _angle[i], direction);
            ctx.rotate(_angle[i]);
            ctx.lineTo(sinner_radius[i], 0);
            ctx.arc(0, 0, sinner_radius[i], 0, -_angle[i], !direction);
            ctx.closePath();
            ctx.rotate(-_angle[i] - _start_angle[i]);
            ctx.translate(-sx[i], -sy[i]);
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
    AnnularWedgeView.prototype._hit_point = function (geometry) {
        var _a, _b;
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        // check radius first
        var x0, y0;
        var x1, y1;
        if (this.model.properties.outer_radius.units == "data") {
            x0 = x - this.max_outer_radius;
            x1 = x + this.max_outer_radius;
            y0 = y - this.max_outer_radius;
            y1 = y + this.max_outer_radius;
        }
        else {
            var sx0 = sx - this.max_outer_radius;
            var sx1 = sx + this.max_outer_radius;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
            var sy0 = sy - this.max_outer_radius;
            var sy1 = sy + this.max_outer_radius;
            _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        }
        var candidates = [];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        for (var _i = 0, _c = this.index.indices(bbox); _i < _c.length; _i++) {
            var i = _c[_i];
            var or2 = Math.pow(this.souter_radius[i], 2);
            var ir2 = Math.pow(this.sinner_radius[i], 2);
            var _d = this.renderer.xscale.r_compute(x, this._x[i]), sx0 = _d[0], sx1 = _d[1];
            var _e = this.renderer.yscale.r_compute(y, this._y[i]), sy0 = _e[0], sy1 = _e[1];
            var dist = Math.pow(sx0 - sx1, 2) + Math.pow(sy0 - sy1, 2);
            if (dist <= or2 && dist >= ir2)
                candidates.push([i, dist]);
        }
        var direction = this.model.properties.direction.value();
        var hits = [];
        for (var _f = 0, candidates_1 = candidates; _f < candidates_1.length; _f++) {
            var _g = candidates_1[_f], i = _g[0], dist = _g[1];
            // NOTE: minus the angle because JS uses non-mathy convention for angles
            var angle = Math.atan2(sy - this.sy[i], sx - this.sx[i]);
            if (math_1.angle_between(-angle, -this._start_angle[i], -this._end_angle[i], direction)) {
                hits.push([i, dist]);
            }
        }
        return hittest.create_hit_test_result_from_hits(hits);
    };
    AnnularWedgeView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    AnnularWedgeView.prototype._scenterxy = function (i) {
        var r = (this.sinner_radius[i] + this.souter_radius[i]) / 2;
        var a = (this._start_angle[i] + this._end_angle[i]) / 2;
        return { x: this.sx[i] + (r * Math.cos(a)), y: this.sy[i] + (r * Math.sin(a)) };
    };
    AnnularWedgeView.prototype.scenterx = function (i) {
        return this._scenterxy(i).x;
    };
    AnnularWedgeView.prototype.scentery = function (i) {
        return this._scenterxy(i).y;
    };
    return AnnularWedgeView;
}(xy_glyph_1.XYGlyphView));
exports.AnnularWedgeView = AnnularWedgeView;
var AnnularWedge = /** @class */ (function (_super) {
    tslib_1.__extends(AnnularWedge, _super);
    function AnnularWedge(attrs) {
        return _super.call(this, attrs) || this;
    }
    AnnularWedge.initClass = function () {
        this.prototype.type = 'AnnularWedge';
        this.prototype.default_view = AnnularWedgeView;
        this.mixins(['line', 'fill']);
        this.define({
            direction: [p.Direction, 'anticlock'],
            inner_radius: [p.DistanceSpec],
            outer_radius: [p.DistanceSpec],
            start_angle: [p.AngleSpec],
            end_angle: [p.AngleSpec],
        });
    };
    return AnnularWedge;
}(xy_glyph_1.XYGlyph));
exports.AnnularWedge = AnnularWedge;
AnnularWedge.initClass();
