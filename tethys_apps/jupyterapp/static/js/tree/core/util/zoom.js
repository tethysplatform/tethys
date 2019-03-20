"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var math_1 = require("./math");
// Module for zoom-related functions
function scale_highlow(range, factor, center) {
    var _a = [range.start, range.end], low = _a[0], high = _a[1];
    var x = center != null ? center : (high + low) / 2.0;
    var x0 = low - (low - x) * factor;
    var x1 = high - (high - x) * factor;
    return [x0, x1];
}
exports.scale_highlow = scale_highlow;
function get_info(scales, _a) {
    var sxy0 = _a[0], sxy1 = _a[1];
    var info = {};
    for (var name_1 in scales) {
        var scale = scales[name_1];
        var _b = scale.r_invert(sxy0, sxy1), start = _b[0], end = _b[1];
        info[name_1] = { start: start, end: end };
    }
    return info;
}
exports.get_info = get_info;
function scale_range(frame, factor, h_axis, v_axis, center) {
    /*
     * Utility function for zoom tools to calculate/create the zoom_info object
     * of the form required by ``PlotCanvasView.update_range``
     *
     * Parameters:
     *   frame : CartesianFrame
     *   factor : Number
     *   h_axis : Boolean, optional
     *     whether to zoom the horizontal axis (default = true)
     *   v_axis : Boolean, optional
     *     whether to zoom the horizontal axis (default = true)
     *   center : object, optional
     *     of form {'x': Number, 'y', Number}
     *
     * Returns:
     *   object:
     */
    if (h_axis === void 0) { h_axis = true; }
    if (v_axis === void 0) { v_axis = true; }
    // clamp the  magnitude of factor, if it is > 1 bad things happen
    factor = math_1.clamp(factor, -0.9, 0.9);
    var hfactor = h_axis ? factor : 0;
    var _a = scale_highlow(frame.bbox.h_range, hfactor, center != null ? center.x : undefined), sx0 = _a[0], sx1 = _a[1];
    var xrs = get_info(frame.xscales, [sx0, sx1]);
    var vfactor = v_axis ? factor : 0;
    var _b = scale_highlow(frame.bbox.v_range, vfactor, center != null ? center.y : undefined), sy0 = _b[0], sy1 = _b[1];
    var yrs = get_info(frame.yscales, [sy0, sy1]);
    // OK this sucks we can't set factor independently in each direction. It is used
    // for GMap plots, and GMap plots always preserve aspect, so effective the value
    // of 'dimensions' is ignored.
    return {
        xrs: xrs,
        yrs: yrs,
        factor: factor,
    };
}
exports.scale_range = scale_range;
