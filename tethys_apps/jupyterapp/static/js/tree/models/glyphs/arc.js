"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var p = require("core/properties");
var ArcView = /** @class */ (function (_super) {
    tslib_1.__extends(ArcView, _super);
    function ArcView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ArcView.prototype._map_data = function () {
        if (this.model.properties.radius.units == "data")
            this.sradius = this.sdist(this.renderer.xscale, this._x, this._radius);
        else
            this.sradius = this._radius;
    };
    ArcView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sradius = _a.sradius, _start_angle = _a._start_angle, _end_angle = _a._end_angle;
        if (this.visuals.line.doit) {
            var direction = this.model.properties.direction.value();
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (isNaN(sx[i] + sy[i] + sradius[i] + _start_angle[i] + _end_angle[i]))
                    continue;
                ctx.beginPath();
                ctx.arc(sx[i], sy[i], sradius[i], _start_angle[i], _end_angle[i], direction);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    ArcView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    return ArcView;
}(xy_glyph_1.XYGlyphView));
exports.ArcView = ArcView;
var Arc = /** @class */ (function (_super) {
    tslib_1.__extends(Arc, _super);
    function Arc(attrs) {
        return _super.call(this, attrs) || this;
    }
    Arc.initClass = function () {
        this.prototype.type = 'Arc';
        this.prototype.default_view = ArcView;
        this.mixins(['line']);
        this.define({
            direction: [p.Direction, 'anticlock'],
            radius: [p.DistanceSpec],
            start_angle: [p.AngleSpec],
            end_angle: [p.AngleSpec],
        });
    };
    return Arc;
}(xy_glyph_1.XYGlyph));
exports.Arc = Arc;
Arc.initClass();
