"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var hittest = require("core/hittest");
var p = require("core/properties");
var array_1 = require("core/util/array");
var arrayable_1 = require("core/util/arrayable");
var CircleView = /** @class */ (function (_super) {
    tslib_1.__extends(CircleView, _super);
    function CircleView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CircleView.prototype._map_data = function () {
        // XXX: Order is important here: size is always present (at least
        // a default), but radius is only present if a user specifies it.
        if (this._radius != null) {
            if (this.model.properties.radius.spec.units == "data") {
                var rd = this.model.properties.radius_dimension.spec.value;
                switch (rd) {
                    case "x": {
                        this.sradius = this.sdist(this.renderer.xscale, this._x, this._radius);
                        break;
                    }
                    case "y": {
                        this.sradius = this.sdist(this.renderer.yscale, this._y, this._radius);
                        break;
                    }
                }
            }
            else {
                this.sradius = this._radius;
                this.max_size = 2 * this.max_radius;
            }
        }
        else
            this.sradius = arrayable_1.map(this._size, function (s) { return s / 2; });
    };
    CircleView.prototype._mask_data = function () {
        var _a, _b, _c, _d;
        var _e = this.renderer.plot_view.frame.bbox.ranges, hr = _e[0], vr = _e[1];
        var x0, y0;
        var x1, y1;
        if (this._radius != null && this.model.properties.radius.units == "data") {
            var sx0 = hr.start;
            var sx1 = hr.end;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
            x0 -= this.max_radius;
            x1 += this.max_radius;
            var sy0 = vr.start;
            var sy1 = vr.end;
            _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
            y0 -= this.max_radius;
            y1 += this.max_radius;
        }
        else {
            var sx0 = hr.start - this.max_size;
            var sx1 = hr.end + this.max_size;
            _c = this.renderer.xscale.r_invert(sx0, sx1), x0 = _c[0], x1 = _c[1];
            var sy0 = vr.start - this.max_size;
            var sy1 = vr.end + this.max_size;
            _d = this.renderer.yscale.r_invert(sy0, sy1), y0 = _d[0], y1 = _d[1];
        }
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        return this.index.indices(bbox);
    };
    CircleView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sradius = _a.sradius;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + sradius[i]))
                continue;
            ctx.beginPath();
            ctx.arc(sx[i], sy[i], sradius[i], 0, 2 * Math.PI, false);
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
    CircleView.prototype._hit_point = function (geometry) {
        var _a, _b, _c, _d, _e, _f;
        var dist, r2, sx0, sx1, sy0, sy1, x0, x1, y0, y1;
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        // check radius first
        if ((this._radius != null) && (this.model.properties.radius.units == "data")) {
            x0 = x - this.max_radius;
            x1 = x + this.max_radius;
            y0 = y - this.max_radius;
            y1 = y + this.max_radius;
        }
        else {
            sx0 = sx - this.max_size;
            sx1 = sx + this.max_size;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
            _b = [Math.min(x0, x1), Math.max(x0, x1)], x0 = _b[0], x1 = _b[1];
            sy0 = sy - this.max_size;
            sy1 = sy + this.max_size;
            _c = this.renderer.yscale.r_invert(sy0, sy1), y0 = _c[0], y1 = _c[1];
            _d = [Math.min(y0, y1), Math.max(y0, y1)], y0 = _d[0], y1 = _d[1];
        }
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var candidates = this.index.indices(bbox);
        var hits = [];
        if ((this._radius != null) && (this.model.properties.radius.units == "data")) {
            for (var _i = 0, candidates_1 = candidates; _i < candidates_1.length; _i++) {
                var i = candidates_1[_i];
                r2 = Math.pow(this.sradius[i], 2);
                _e = this.renderer.xscale.r_compute(x, this._x[i]), sx0 = _e[0], sx1 = _e[1];
                _f = this.renderer.yscale.r_compute(y, this._y[i]), sy0 = _f[0], sy1 = _f[1];
                dist = Math.pow(sx0 - sx1, 2) + Math.pow(sy0 - sy1, 2);
                if (dist <= r2) {
                    hits.push([i, dist]);
                }
            }
        }
        else {
            for (var _g = 0, candidates_2 = candidates; _g < candidates_2.length; _g++) {
                var i = candidates_2[_g];
                r2 = Math.pow(this.sradius[i], 2);
                dist = Math.pow(this.sx[i] - sx, 2) + Math.pow(this.sy[i] - sy, 2);
                if (dist <= r2) {
                    hits.push([i, dist]);
                }
            }
        }
        return hittest.create_hit_test_result_from_hits(hits);
    };
    CircleView.prototype._hit_span = function (geometry) {
        var _a, _b, _c, _d;
        var ms, x0, x1, y0, y1;
        var sx = geometry.sx, sy = geometry.sy;
        var _e = this.bounds(), minX = _e.minX, minY = _e.minY, maxX = _e.maxX, maxY = _e.maxY;
        var result = hittest.create_empty_hit_test_result();
        if (geometry.direction == 'h') {
            // use circle bounds instead of current pointer y coordinates
            var sx0 = void 0, sx1 = void 0;
            y0 = minY;
            y1 = maxY;
            if (this._radius != null && this.model.properties.radius.units == "data") {
                sx0 = sx - this.max_radius;
                sx1 = sx + this.max_radius;
                _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
            }
            else {
                ms = this.max_size / 2;
                sx0 = sx - ms;
                sx1 = sx + ms;
                _b = this.renderer.xscale.r_invert(sx0, sx1), x0 = _b[0], x1 = _b[1];
            }
        }
        else {
            // use circle bounds instead of current pointer x coordinates
            var sy0 = void 0, sy1 = void 0;
            x0 = minX;
            x1 = maxX;
            if (this._radius != null && this.model.properties.radius.units == "data") {
                sy0 = sy - this.max_radius;
                sy1 = sy + this.max_radius;
                _c = this.renderer.yscale.r_invert(sy0, sy1), y0 = _c[0], y1 = _c[1];
            }
            else {
                ms = this.max_size / 2;
                sy0 = sy - ms;
                sy1 = sy + ms;
                _d = this.renderer.yscale.r_invert(sy0, sy1), y0 = _d[0], y1 = _d[1];
            }
        }
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var hits = this.index.indices(bbox);
        result.indices = hits;
        return result;
    };
    CircleView.prototype._hit_rect = function (geometry) {
        var sx0 = geometry.sx0, sx1 = geometry.sx1, sy0 = geometry.sy0, sy1 = geometry.sy1;
        var _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var result = hittest.create_empty_hit_test_result();
        result.indices = this.index.indices(bbox);
        return result;
    };
    CircleView.prototype._hit_poly = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        // TODO (bev) use spatial index to pare candidate list
        var candidates = array_1.range(0, this.sx.length);
        var hits = [];
        for (var i = 0, end = candidates.length; i < end; i++) {
            var idx = candidates[i];
            if (hittest.point_in_poly(this.sx[i], this.sy[i], sx, sy)) {
                hits.push(idx);
            }
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    // circle does not inherit from marker (since it also accepts radius) so we
    // must supply a draw_legend for it  here
    CircleView.prototype.draw_legend_for_index = function (ctx, _a, index) {
        var x0 = _a.x0, y0 = _a.y0, x1 = _a.x1, y1 = _a.y1;
        // using objects like this seems a little wonky, since the keys are coerced to
        // stings, but it works
        var len = index + 1;
        var sx = new Array(len);
        sx[index] = (x0 + x1) / 2;
        var sy = new Array(len);
        sy[index] = (y0 + y1) / 2;
        var sradius = new Array(len);
        sradius[index] = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.2;
        this._render(ctx, [index], { sx: sx, sy: sy, sradius: sradius }); // XXX
    };
    return CircleView;
}(xy_glyph_1.XYGlyphView));
exports.CircleView = CircleView;
var Circle = /** @class */ (function (_super) {
    tslib_1.__extends(Circle, _super);
    function Circle(attrs) {
        return _super.call(this, attrs) || this;
    }
    Circle.initClass = function () {
        this.prototype.type = 'Circle';
        this.prototype.default_view = CircleView;
        this.mixins(['line', 'fill']);
        this.define({
            angle: [p.AngleSpec, 0],
            size: [p.DistanceSpec, { units: "screen", value: 4 }],
            radius: [p.DistanceSpec, null],
            radius_dimension: [p.String, 'x'],
        });
    };
    Circle.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.properties.radius.optional = true;
    };
    return Circle;
}(xy_glyph_1.XYGlyph));
exports.Circle = Circle;
Circle.initClass();
