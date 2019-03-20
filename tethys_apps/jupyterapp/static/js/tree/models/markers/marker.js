"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("../glyphs/xy_glyph");
var hittest = require("core/hittest");
var p = require("core/properties");
var array_1 = require("core/util/array");
var MarkerView = /** @class */ (function (_super) {
    tslib_1.__extends(MarkerView, _super);
    function MarkerView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MarkerView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, _size = _a._size, _angle = _a._angle;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + _size[i] + _angle[i]))
                continue;
            var r = _size[i] / 2;
            ctx.beginPath();
            ctx.translate(sx[i], sy[i]);
            if (_angle[i])
                ctx.rotate(_angle[i]);
            this._render_one(ctx, i, r, this.visuals.line, this.visuals.fill);
            if (_angle[i])
                ctx.rotate(-_angle[i]);
            ctx.translate(-sx[i], -sy[i]);
        }
    };
    MarkerView.prototype._mask_data = function () {
        // dilate the inner screen region by max_size and map back to data space for use in
        // spatial query
        var hr = this.renderer.plot_view.frame.bbox.h_range;
        var sx0 = hr.start - this.max_size;
        var sx1 = hr.end + this.max_size;
        var _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var vr = this.renderer.plot_view.frame.bbox.v_range;
        var sy0 = vr.start - this.max_size;
        var sy1 = vr.end + this.max_size;
        var _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        return this.index.indices(bbox);
    };
    MarkerView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var sx0 = sx - this.max_size;
        var sx1 = sx + this.max_size;
        var _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var sy0 = sy - this.max_size;
        var sy1 = sy + this.max_size;
        var _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var candidates = this.index.indices(bbox);
        var hits = [];
        for (var _i = 0, candidates_1 = candidates; _i < candidates_1.length; _i++) {
            var i = candidates_1[_i];
            var s2 = this._size[i] / 2;
            var dist = Math.abs(this.sx[i] - sx) + Math.abs(this.sy[i] - sy);
            if (Math.abs(this.sx[i] - sx) <= s2 && Math.abs(this.sy[i] - sy) <= s2) {
                hits.push([i, dist]);
            }
        }
        return hittest.create_hit_test_result_from_hits(hits);
    };
    MarkerView.prototype._hit_span = function (geometry) {
        var _a, _b;
        var sx = geometry.sx, sy = geometry.sy;
        var _c = this.bounds(), minX = _c.minX, minY = _c.minY, maxX = _c.maxX, maxY = _c.maxY;
        var result = hittest.create_empty_hit_test_result();
        var x0, x1;
        var y0, y1;
        if (geometry.direction == 'h') {
            y0 = minY;
            y1 = maxY;
            var ms = this.max_size / 2;
            var sx0 = sx - ms;
            var sx1 = sx + ms;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        }
        else {
            x0 = minX;
            x1 = maxX;
            var ms = this.max_size / 2;
            var sy0 = sy - ms;
            var sy1 = sy + ms;
            _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        }
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var hits = this.index.indices(bbox);
        result.indices = hits;
        return result;
    };
    MarkerView.prototype._hit_rect = function (geometry) {
        var sx0 = geometry.sx0, sx1 = geometry.sx1, sy0 = geometry.sy0, sy1 = geometry.sy1;
        var _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var result = hittest.create_empty_hit_test_result();
        result.indices = this.index.indices(bbox);
        return result;
    };
    MarkerView.prototype._hit_poly = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        // TODO (bev) use spatial index to pare candidate list
        var candidates = array_1.range(0, this.sx.length);
        var hits = [];
        for (var i = 0, end = candidates.length; i < end; i++) {
            var idx = candidates[i];
            if (hittest.point_in_poly(this.sx[i], this.sy[i], sx, sy))
                hits.push(idx);
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    MarkerView.prototype.draw_legend_for_index = function (ctx, _a, index) {
        var x0 = _a.x0, x1 = _a.x1, y0 = _a.y0, y1 = _a.y1;
        // using objects like this seems a little wonky, since the keys are coerced to
        // stings, but it works
        var len = index + 1;
        var sx = new Array(len);
        sx[index] = (x0 + x1) / 2;
        var sy = new Array(len);
        sy[index] = (y0 + y1) / 2;
        var size = new Array(len);
        size[index] = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.4;
        var angle = new Array(len);
        angle[index] = 0; // don't attempt to match glyph angle
        this._render(ctx, [index], { sx: sx, sy: sy, _size: size, _angle: angle }); // XXX
    };
    return MarkerView;
}(xy_glyph_1.XYGlyphView));
exports.MarkerView = MarkerView;
var Marker = /** @class */ (function (_super) {
    tslib_1.__extends(Marker, _super);
    function Marker(attrs) {
        return _super.call(this, attrs) || this;
    }
    Marker.initClass = function () {
        this.mixins(['line', 'fill']);
        this.define({
            size: [p.DistanceSpec, { units: "screen", value: 4 }],
            angle: [p.AngleSpec, 0],
        });
    };
    return Marker;
}(xy_glyph_1.XYGlyph));
exports.Marker = Marker;
Marker.initClass();
