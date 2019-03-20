"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var hittest = require("core/hittest");
var LineView = /** @class */ (function (_super) {
    tslib_1.__extends(LineView, _super);
    function LineView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LineView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy;
        var drawing = false;
        var last_index = null;
        this.visuals.line.set_value(ctx);
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (drawing) {
                if (!isFinite(sx[i] + sy[i])) {
                    ctx.stroke();
                    ctx.beginPath();
                    drawing = false;
                    last_index = i;
                    continue;
                }
                if (last_index != null && i - last_index > 1) {
                    ctx.stroke();
                    drawing = false;
                }
            }
            if (drawing)
                ctx.lineTo(sx[i], sy[i]);
            else {
                ctx.beginPath();
                ctx.moveTo(sx[i], sy[i]);
                drawing = true;
            }
            last_index = i;
        }
        if (drawing)
            ctx.stroke();
    };
    LineView.prototype._hit_point = function (geometry) {
        var _this = this;
        /* Check if the point geometry hits this line glyph and return an object
        that describes the hit result:
          Args:
            * geometry (object): object with the following keys
              * sx (float): screen x coordinate of the point
              * sy (float): screen y coordinate of the point
              * type (str): type of geometry (in this case it's a point)
          Output:
            Object with the following keys:
              * 0d (bool): whether the point hits the glyph or not
              * 1d (array(int)): array with the indices hit by the point
        */
        var result = hittest.create_empty_hit_test_result();
        var point = { x: geometry.sx, y: geometry.sy };
        var shortest = 9999;
        var threshold = Math.max(2, this.visuals.line.line_width.value() / 2);
        for (var i = 0, end = this.sx.length - 1; i < end; i++) {
            var p0 = { x: this.sx[i], y: this.sy[i] };
            var p1 = { x: this.sx[i + 1], y: this.sy[i + 1] };
            var dist = hittest.dist_to_segment(point, p0, p1);
            if (dist < threshold && dist < shortest) {
                shortest = dist;
                result.add_to_selected_glyphs(this.model);
                result.get_view = function () { return _this; };
                result.line_indices = [i];
            }
        }
        return result;
    };
    LineView.prototype._hit_span = function (geometry) {
        var _this = this;
        var sx = geometry.sx, sy = geometry.sy;
        var result = hittest.create_empty_hit_test_result();
        var val;
        var values;
        if (geometry.direction == 'v') {
            val = this.renderer.yscale.invert(sy);
            values = this._y;
        }
        else {
            val = this.renderer.xscale.invert(sx);
            values = this._x;
        }
        for (var i = 0, end = values.length - 1; i < end; i++) {
            if ((values[i] <= val && val <= values[i + 1]) || (values[i + 1] <= val && val <= values[i])) {
                result.add_to_selected_glyphs(this.model);
                result.get_view = function () { return _this; };
                result.line_indices.push(i);
            }
        }
        return result;
    };
    LineView.prototype.get_interpolation_hit = function (i, geometry) {
        var _a = [this._x[i], this._y[i], this._x[i + 1], this._y[i + 1]], x2 = _a[0], y2 = _a[1], x3 = _a[2], y3 = _a[3];
        return utils_1.line_interpolation(this.renderer, geometry, x2, y2, x3, y3);
    };
    LineView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    return LineView;
}(xy_glyph_1.XYGlyphView));
exports.LineView = LineView;
var Line = /** @class */ (function (_super) {
    tslib_1.__extends(Line, _super);
    function Line(attrs) {
        return _super.call(this, attrs) || this;
    }
    Line.initClass = function () {
        this.prototype.type = 'Line';
        this.prototype.default_view = LineView;
        this.mixins(['line']);
    };
    return Line;
}(xy_glyph_1.XYGlyph));
exports.Line = Line;
Line.initClass();
