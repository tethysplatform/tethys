"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var utils_1 = require("./utils");
var p = require("core/properties");
var StepView = /** @class */ (function (_super) {
    tslib_1.__extends(StepView, _super);
    function StepView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    StepView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy;
        var _b, _c, _d, _e, _f, _g;
        var drawing = false;
        var last_index = null;
        this.visuals.line.set_value(ctx);
        var L = indices.length;
        if (L < 2)
            return;
        ctx.beginPath();
        ctx.moveTo(sx[0], sy[0]);
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            var x1 = void 0, x2 = void 0;
            var y1 = void 0, y2 = void 0;
            switch (this.model.mode) {
                case "before": {
                    ;
                    _b = [sx[i - 1], sy[i]], x1 = _b[0], y1 = _b[1];
                    _c = [sx[i], sy[i]], x2 = _c[0], y2 = _c[1];
                    break;
                }
                case "after": {
                    ;
                    _d = [sx[i], sy[i - 1]], x1 = _d[0], y1 = _d[1];
                    _e = [sx[i], sy[i]], x2 = _e[0], y2 = _e[1];
                    break;
                }
                case "center": {
                    var xm = (sx[i - 1] + sx[i]) / 2;
                    _f = [xm, sy[i - 1]], x1 = _f[0], y1 = _f[1];
                    _g = [xm, sy[i]], x2 = _g[0], y2 = _g[1];
                    break;
                }
                default:
                    throw new Error("unexpected");
            }
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
            if (drawing) {
                ctx.lineTo(x1, y1);
                ctx.lineTo(x2, y2);
            }
            else {
                ctx.beginPath();
                ctx.moveTo(sx[i], sy[i]);
                drawing = true;
            }
            last_index = i;
        }
        ctx.lineTo(sx[L - 1], sy[L - 1]);
        ctx.stroke();
    };
    StepView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    return StepView;
}(xy_glyph_1.XYGlyphView));
exports.StepView = StepView;
var Step = /** @class */ (function (_super) {
    tslib_1.__extends(Step, _super);
    function Step(attrs) {
        return _super.call(this, attrs) || this;
    }
    Step.initClass = function () {
        this.prototype.type = 'Step';
        this.prototype.default_view = StepView;
        this.mixins(['line']);
        this.define({
            mode: [p.StepMode, "before"],
        });
    };
    return Step;
}(xy_glyph_1.XYGlyph));
exports.Step = Step;
Step.initClass();
