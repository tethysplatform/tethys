"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var marker_1 = require("./marker");
var defs_1 = require("./defs");
var p = require("core/properties");
var ScatterView = /** @class */ (function (_super) {
    tslib_1.__extends(ScatterView, _super);
    function ScatterView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ScatterView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, _size = _a._size, _angle = _a._angle, _marker = _a._marker;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + _size[i] + _angle[i]))
                continue;
            var r = _size[i] / 2;
            ctx.beginPath();
            ctx.translate(sx[i], sy[i]);
            if (_angle[i])
                ctx.rotate(_angle[i]);
            defs_1.marker_funcs[_marker[i]](ctx, i, r, this.visuals.line, this.visuals.fill);
            if (_angle[i])
                ctx.rotate(-_angle[i]);
            ctx.translate(-sx[i], -sy[i]);
        }
    };
    ScatterView.prototype.draw_legend_for_index = function (ctx, _a, index) {
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
        var marker = new Array(len);
        marker[index] = this._marker[index];
        this._render(ctx, [index], { sx: sx, sy: sy, _size: size, _angle: angle, _marker: marker }); // XXX
    };
    return ScatterView;
}(marker_1.MarkerView));
exports.ScatterView = ScatterView;
var Scatter = /** @class */ (function (_super) {
    tslib_1.__extends(Scatter, _super);
    function Scatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    Scatter.initClass = function () {
        this.prototype.type = 'Scatter';
        this.prototype.default_view = ScatterView;
        this.define({
            marker: [p.MarkerSpec, { value: "circle" }],
        });
    };
    return Scatter;
}(marker_1.Marker));
exports.Scatter = Scatter;
Scatter.initClass();
