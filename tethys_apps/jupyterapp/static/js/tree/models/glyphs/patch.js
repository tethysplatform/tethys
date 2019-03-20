"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var PatchView = /** @class */ (function (_super) {
    tslib_1.__extends(PatchView, _super);
    function PatchView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PatchView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy;
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_value(ctx);
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (i == 0) {
                    ctx.beginPath();
                    ctx.moveTo(sx[i], sy[i]);
                    continue;
                }
                else if (isNaN(sx[i] + sy[i])) {
                    ctx.closePath();
                    ctx.fill();
                    ctx.beginPath();
                    continue;
                }
                else
                    ctx.lineTo(sx[i], sy[i]);
            }
            ctx.closePath();
            ctx.fill();
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_value(ctx);
            for (var _b = 0, indices_2 = indices; _b < indices_2.length; _b++) {
                var i = indices_2[_b];
                if (i == 0) {
                    ctx.beginPath();
                    ctx.moveTo(sx[i], sy[i]);
                    continue;
                }
                else if (isNaN(sx[i] + sy[i])) {
                    ctx.closePath();
                    ctx.stroke();
                    ctx.beginPath();
                    continue;
                }
                else
                    ctx.lineTo(sx[i], sy[i]);
            }
            ctx.closePath();
            return ctx.stroke();
        }
    };
    PatchView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    return PatchView;
}(xy_glyph_1.XYGlyphView));
exports.PatchView = PatchView;
var Patch = /** @class */ (function (_super) {
    tslib_1.__extends(Patch, _super);
    function Patch(attrs) {
        return _super.call(this, attrs) || this;
    }
    Patch.initClass = function () {
        this.prototype.type = 'Patch';
        this.prototype.default_view = PatchView;
        this.mixins(['line', 'fill']);
    };
    return Patch;
}(xy_glyph_1.XYGlyph));
exports.Patch = Patch;
Patch.initClass();
