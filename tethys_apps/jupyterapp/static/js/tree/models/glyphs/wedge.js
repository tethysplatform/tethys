"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var hittest = require("core/hittest");
var p = require("core/properties");
var math_1 = require("core/util/math");
var WedgeView = /** @class */ (function (_super) {
    tslib_1.__extends(WedgeView, _super);
    function WedgeView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WedgeView.prototype._map_data = function () {
        if (this.model.properties.radius.units == "data")
            this.sradius = this.sdist(this.renderer.xscale, this._x, this._radius);
        else
            this.sradius = this._radius;
    };
    WedgeView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sradius = _a.sradius, _start_angle = _a._start_angle, _end_angle = _a._end_angle;
        var direction = this.model.properties.direction.value();
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + sradius[i] + _start_angle[i] + _end_angle[i]))
                continue;
            ctx.beginPath();
            ctx.arc(sx[i], sy[i], sradius[i], _start_angle[i], _end_angle[i], direction);
            ctx.lineTo(sx[i], sy[i]);
            ctx.closePath();
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
    WedgeView.prototype._hit_point = function (geometry) {
        var _a, _b, _c, _d;
        var dist, sx0, sx1, sy0, sy1, x0, x1, y0, y1;
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        // check diameter first
        var max_diameter = 2 * this.max_radius;
        if (this.model.properties.radius.units === "data") {
            x0 = x - max_diameter;
            x1 = x + max_diameter;
            y0 = y - max_diameter;
            y1 = y + max_diameter;
        }
        else {
            sx0 = sx - max_diameter;
            sx1 = sx + max_diameter;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
            sy0 = sy - max_diameter;
            sy1 = sy + max_diameter;
            _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        }
        var candidates = [];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        for (var _i = 0, _e = this.index.indices(bbox); _i < _e.length; _i++) {
            var i = _e[_i];
            var r2 = Math.pow(this.sradius[i], 2);
            _c = this.renderer.xscale.r_compute(x, this._x[i]), sx0 = _c[0], sx1 = _c[1];
            _d = this.renderer.yscale.r_compute(y, this._y[i]), sy0 = _d[0], sy1 = _d[1];
            dist = Math.pow(sx0 - sx1, 2) + Math.pow(sy0 - sy1, 2);
            if (dist <= r2) {
                candidates.push([i, dist]);
            }
        }
        var direction = this.model.properties.direction.value();
        var hits = [];
        for (var _f = 0, candidates_1 = candidates; _f < candidates_1.length; _f++) {
            var _g = candidates_1[_f], i = _g[0], dist_1 = _g[1];
            // NOTE: minus the angle because JS uses non-mathy convention for angles
            var angle = Math.atan2(sy - this.sy[i], sx - this.sx[i]);
            if (math_1.angle_between(-angle, -this._start_angle[i], -this._end_angle[i], direction)) {
                hits.push([i, dist_1]);
            }
        }
        return hittest.create_hit_test_result_from_hits(hits);
    };
    WedgeView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    WedgeView.prototype._scenterxy = function (i) {
        var r = this.sradius[i] / 2;
        var a = (this._start_angle[i] + this._end_angle[i]) / 2;
        return { x: this.sx[i] + (r * Math.cos(a)), y: this.sy[i] + (r * Math.sin(a)) };
    };
    WedgeView.prototype.scenterx = function (i) {
        return this._scenterxy(i).x;
    };
    WedgeView.prototype.scentery = function (i) {
        return this._scenterxy(i).y;
    };
    return WedgeView;
}(xy_glyph_1.XYGlyphView));
exports.WedgeView = WedgeView;
var Wedge = /** @class */ (function (_super) {
    tslib_1.__extends(Wedge, _super);
    function Wedge(attrs) {
        return _super.call(this, attrs) || this;
    }
    Wedge.initClass = function () {
        this.prototype.type = 'Wedge';
        this.prototype.default_view = WedgeView;
        this.mixins(['line', 'fill']);
        this.define({
            direction: [p.Direction, 'anticlock'],
            radius: [p.DistanceSpec],
            start_angle: [p.AngleSpec],
            end_angle: [p.AngleSpec],
        });
    };
    return Wedge;
}(xy_glyph_1.XYGlyph));
exports.Wedge = Wedge;
Wedge.initClass();
