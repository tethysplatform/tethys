"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var hittest = require("core/hittest");
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var utils_1 = require("./utils");
var SegmentView = /** @class */ (function (_super) {
    tslib_1.__extends(SegmentView, _super);
    function SegmentView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SegmentView.prototype._index_data = function () {
        var points = [];
        for (var i = 0, end = this._x0.length; i < end; i++) {
            var x0 = this._x0[i];
            var x1 = this._x1[i];
            var y0 = this._y0[i];
            var y1 = this._y1[i];
            if (!isNaN(x0 + x1 + y0 + y1)) {
                points.push({
                    minX: Math.min(x0, x1),
                    minY: Math.min(y0, y1),
                    maxX: Math.max(x0, x1),
                    maxY: Math.max(y0, y1),
                    i: i,
                });
            }
        }
        return new spatial_1.SpatialIndex(points);
    };
    SegmentView.prototype._render = function (ctx, indices, _a) {
        var sx0 = _a.sx0, sy0 = _a.sy0, sx1 = _a.sx1, sy1 = _a.sy1;
        if (this.visuals.line.doit) {
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (isNaN(sx0[i] + sy0[i] + sx1[i] + sy1[i]))
                    continue;
                ctx.beginPath();
                ctx.moveTo(sx0[i], sy0[i]);
                ctx.lineTo(sx1[i], sy1[i]);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    SegmentView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var point = { x: sx, y: sy };
        var hits = [];
        var lw_voffset = 2; // FIXME: Use maximum of segments line_width/2 instead of magic constant 2
        var _a = this.renderer.xscale.r_invert(sx - lw_voffset, sx + lw_voffset), minX = _a[0], maxX = _a[1];
        var _b = this.renderer.yscale.r_invert(sy - lw_voffset, sy + lw_voffset), minY = _b[0], maxY = _b[1];
        var candidates = this.index.indices({ minX: minX, minY: minY, maxX: maxX, maxY: maxY });
        for (var _i = 0, candidates_1 = candidates; _i < candidates_1.length; _i++) {
            var i = candidates_1[_i];
            var threshold2 = Math.pow(Math.max(2, this.visuals.line.cache_select('line_width', i) / 2), 2);
            var p0 = { x: this.sx0[i], y: this.sy0[i] };
            var p1 = { x: this.sx1[i], y: this.sy1[i] };
            var dist2 = hittest.dist_to_segment_squared(point, p0, p1);
            if (dist2 < threshold2)
                hits.push(i);
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    SegmentView.prototype._hit_span = function (geometry) {
        var _a, _b;
        var _c = this.renderer.plot_view.frame.bbox.ranges, hr = _c[0], vr = _c[1];
        var sx = geometry.sx, sy = geometry.sy;
        var v0;
        var v1;
        var val;
        if (geometry.direction == 'v') {
            val = this.renderer.yscale.invert(sy);
            _a = [this._y0, this._y1], v0 = _a[0], v1 = _a[1];
        }
        else {
            val = this.renderer.xscale.invert(sx);
            _b = [this._x0, this._x1], v0 = _b[0], v1 = _b[1];
        }
        var hits = [];
        var _d = this.renderer.xscale.r_invert(hr.start, hr.end), minX = _d[0], maxX = _d[1];
        var _e = this.renderer.yscale.r_invert(vr.start, vr.end), minY = _e[0], maxY = _e[1];
        var candidates = this.index.indices({ minX: minX, minY: minY, maxX: maxX, maxY: maxY });
        for (var _i = 0, candidates_2 = candidates; _i < candidates_2.length; _i++) {
            var i = candidates_2[_i];
            if ((v0[i] <= val && val <= v1[i]) || (v1[i] <= val && val <= v0[i]))
                hits.push(i);
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    SegmentView.prototype.scenterx = function (i) {
        return (this.sx0[i] + this.sx1[i]) / 2;
    };
    SegmentView.prototype.scentery = function (i) {
        return (this.sy0[i] + this.sy1[i]) / 2;
    };
    SegmentView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    return SegmentView;
}(glyph_1.GlyphView));
exports.SegmentView = SegmentView;
var Segment = /** @class */ (function (_super) {
    tslib_1.__extends(Segment, _super);
    function Segment(attrs) {
        return _super.call(this, attrs) || this;
    }
    Segment.initClass = function () {
        this.prototype.type = 'Segment';
        this.prototype.default_view = SegmentView;
        this.coords([['x0', 'y0'], ['x1', 'y1']]);
        this.mixins(['line']);
    };
    return Segment;
}(glyph_1.Glyph));
exports.Segment = Segment;
Segment.initClass();
