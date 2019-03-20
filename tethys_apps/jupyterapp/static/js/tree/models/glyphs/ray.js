"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var p = require("core/properties");
var RayView = /** @class */ (function (_super) {
    tslib_1.__extends(RayView, _super);
    function RayView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RayView.prototype._map_data = function () {
        if (this.model.properties.length.units == "data")
            this.slength = this.sdist(this.renderer.xscale, this._x, this._length);
        else
            this.slength = this._length;
    };
    RayView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, slength = _a.slength, _angle = _a._angle;
        if (this.visuals.line.doit) {
            var width = this.renderer.plot_view.frame._width.value;
            var height = this.renderer.plot_view.frame._height.value;
            var inf_len = 2 * (width + height);
            for (var i = 0, end = slength.length; i < end; i++) {
                if (slength[i] == 0)
                    slength[i] = inf_len;
            }
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (isNaN(sx[i] + sy[i] + _angle[i] + slength[i]))
                    continue;
                ctx.translate(sx[i], sy[i]);
                ctx.rotate(_angle[i]);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(slength[i], 0);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
                ctx.rotate(-_angle[i]);
                ctx.translate(-sx[i], -sy[i]);
            }
        }
    };
    RayView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    return RayView;
}(xy_glyph_1.XYGlyphView));
exports.RayView = RayView;
var Ray = /** @class */ (function (_super) {
    tslib_1.__extends(Ray, _super);
    function Ray(attrs) {
        return _super.call(this, attrs) || this;
    }
    Ray.initClass = function () {
        this.prototype.type = 'Ray';
        this.prototype.default_view = RayView;
        this.mixins(['line']);
        this.define({
            length: [p.DistanceSpec],
            angle: [p.AngleSpec],
        });
    };
    return Ray;
}(xy_glyph_1.XYGlyph));
exports.Ray = Ray;
Ray.initClass();
