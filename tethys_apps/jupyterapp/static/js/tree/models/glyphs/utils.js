"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var hittest = require("core/hittest");
function generic_line_legend(visuals, ctx, _a, index) {
    var x0 = _a.x0, x1 = _a.x1, y0 = _a.y0, y1 = _a.y1;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x0, (y0 + y1) / 2);
    ctx.lineTo(x1, (y0 + y1) / 2);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, index);
        ctx.stroke();
    }
    ctx.restore();
}
exports.generic_line_legend = generic_line_legend;
function generic_area_legend(visuals, ctx, _a, index) {
    var x0 = _a.x0, x1 = _a.x1, y0 = _a.y0, y1 = _a.y1;
    var w = Math.abs(x1 - x0);
    var dw = w * 0.1;
    var h = Math.abs(y1 - y0);
    var dh = h * 0.1;
    var sx0 = x0 + dw;
    var sx1 = x1 - dw;
    var sy0 = y0 + dh;
    var sy1 = y1 - dh;
    if (visuals.fill.doit) {
        visuals.fill.set_vectorize(ctx, index);
        ctx.fillRect(sx0, sy0, sx1 - sx0, sy1 - sy0);
    }
    if (visuals.line.doit) {
        ctx.beginPath();
        ctx.rect(sx0, sy0, sx1 - sx0, sy1 - sy0);
        visuals.line.set_vectorize(ctx, index);
        ctx.stroke();
    }
}
exports.generic_area_legend = generic_area_legend;
function line_interpolation(renderer, geometry, x2, y2, x3, y3) {
    var _a, _b, _c, _d, _e, _f;
    var sx = geometry.sx, sy = geometry.sy;
    var x0, x1;
    var y0, y1;
    if (geometry.type == 'point') {
        // The +/- adjustments here are to dilate the hit point into a virtual "segment" to use below
        ;
        _a = renderer.yscale.r_invert(sy - 1, sy + 1), y0 = _a[0], y1 = _a[1];
        _b = renderer.xscale.r_invert(sx - 1, sx + 1), x0 = _b[0], x1 = _b[1];
    }
    else {
        // The +/- adjustments here are to handle cases such as purely horizontal or vertical lines
        if (geometry.direction == 'v') {
            ;
            _c = renderer.yscale.r_invert(sy, sy), y0 = _c[0], y1 = _c[1];
            _d = [Math.min(x2 - 1, x3 - 1), Math.max(x2 + 1, x3 + 1)], x0 = _d[0], x1 = _d[1];
        }
        else {
            ;
            _e = renderer.xscale.r_invert(sx, sx), x0 = _e[0], x1 = _e[1];
            _f = [Math.min(y2 - 1, y3 - 1), Math.max(y2 + 1, y3 + 1)], y0 = _f[0], y1 = _f[1];
        }
    }
    var _g = hittest.check_2_segments_intersect(x0, y0, x1, y1, x2, y2, x3, y3), x = _g.x, y = _g.y;
    return [x, y]; // XXX: null is not handled at use sites
}
exports.line_interpolation = line_interpolation;
