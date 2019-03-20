"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var utils_1 = require("./utils");
var hittest = require("core/hittest");
var BoxView = /** @class */ (function (_super) {
    tslib_1.__extends(BoxView, _super);
    function BoxView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BoxView.prototype._index_box = function (len) {
        var points = [];
        for (var i = 0; i < len; i++) {
            var _a = this._lrtb(i), l = _a[0], r = _a[1], t = _a[2], b = _a[3];
            if (isNaN(l + r + t + b) || !isFinite(l + r + t + b))
                continue;
            points.push({ minX: l, minY: b, maxX: r, maxY: t, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    BoxView.prototype._render = function (ctx, indices, _a) {
        var sleft = _a.sleft, sright = _a.sright, stop = _a.stop, sbottom = _a.sbottom;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sleft[i] + stop[i] + sright[i] + sbottom[i]))
                continue;
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                ctx.fillRect(sleft[i], stop[i], sright[i] - sleft[i], sbottom[i] - stop[i]);
            }
            if (this.visuals.line.doit) {
                ctx.beginPath();
                ctx.rect(sleft[i], stop[i], sright[i] - sleft[i], sbottom[i] - stop[i]);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    // We need to clamp the endpoints inside the viewport, because various browser canvas
    // implementations have issues drawing rects with enpoints far outside the viewport
    BoxView.prototype._clamp_viewport = function () {
        var hr = this.renderer.plot_view.frame.bbox.h_range;
        var vr = this.renderer.plot_view.frame.bbox.v_range;
        var n = this.stop.length;
        for (var i = 0; i < n; i++) {
            this.stop[i] = Math.max(this.stop[i], vr.start);
            this.sbottom[i] = Math.min(this.sbottom[i], vr.end);
            this.sleft[i] = Math.max(this.sleft[i], hr.start);
            this.sright[i] = Math.min(this.sright[i], hr.end);
        }
    };
    BoxView.prototype._hit_rect = function (geometry) {
        return this._hit_rect_against_index(geometry);
    };
    BoxView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        var hits = this.index.indices({ minX: x, minY: y, maxX: x, maxY: y });
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    BoxView.prototype._hit_span = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var hits;
        if (geometry.direction == 'v') {
            var y = this.renderer.yscale.invert(sy);
            var hr = this.renderer.plot_view.frame.bbox.h_range;
            var _a = this.renderer.xscale.r_invert(hr.start, hr.end), minX = _a[0], maxX = _a[1];
            hits = this.index.indices({ minX: minX, minY: y, maxX: maxX, maxY: y });
        }
        else {
            var x = this.renderer.xscale.invert(sx);
            var vr = this.renderer.plot_view.frame.bbox.v_range;
            var _b = this.renderer.yscale.r_invert(vr.start, vr.end), minY = _b[0], maxY = _b[1];
            hits = this.index.indices({ minX: x, minY: minY, maxX: x, maxY: maxY });
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    BoxView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    return BoxView;
}(glyph_1.GlyphView));
exports.BoxView = BoxView;
var Box = /** @class */ (function (_super) {
    tslib_1.__extends(Box, _super);
    function Box(attrs) {
        return _super.call(this, attrs) || this;
    }
    Box.initClass = function () {
        this.prototype.type = "Box";
        this.mixins(['line', 'fill']);
    };
    return Box;
}(glyph_1.Glyph));
exports.Box = Box;
Box.initClass();
