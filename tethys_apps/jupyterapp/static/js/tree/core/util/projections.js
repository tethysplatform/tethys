"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var proj4 = require("proj4/lib/core");
var Projection = require("proj4/lib/Proj");
var mercator = new Projection('GOOGLE');
var wgs84 = new Projection('WGS84');
exports.wgs84_mercator = proj4(wgs84, mercator);
var mercator_bounds = {
    lon: [-20026376.39, 20026376.39],
    lat: [-20048966.10, 20048966.10],
};
var latlon_bounds = {
    lon: [-180, 180],
    lat: [-85.06, 85.06],
};
function clip_mercator(low, high, dimension) {
    var _a = mercator_bounds[dimension], min = _a[0], max = _a[1];
    return [Math.max(low, min), Math.min(high, max)];
}
exports.clip_mercator = clip_mercator;
function in_bounds(value, dimension) {
    return value > latlon_bounds[dimension][0] && value < latlon_bounds[dimension][1];
}
exports.in_bounds = in_bounds;
function project_xy(x, y) {
    var n = Math.min(x.length, y.length);
    var merc_x_s = new Array(n);
    var merc_y_s = new Array(n);
    for (var i = 0; i < n; i++) {
        var _a = exports.wgs84_mercator.forward([x[i], y[i]]), merc_x = _a[0], merc_y = _a[1];
        merc_x_s[i] = merc_x;
        merc_y_s[i] = merc_y;
    }
    return [merc_x_s, merc_y_s];
}
exports.project_xy = project_xy;
function project_xsys(xs, ys) {
    var n = Math.min(xs.length, ys.length);
    var merc_xs_s = new Array(n);
    var merc_ys_s = new Array(n);
    for (var i = 0; i < n; i++) {
        var _a = project_xy(xs[i], ys[i]), merc_x_s = _a[0], merc_y_s = _a[1];
        merc_xs_s[i] = merc_x_s;
        merc_ys_s[i] = merc_y_s;
    }
    return [merc_xs_s, merc_ys_s];
}
exports.project_xsys = project_xsys;
