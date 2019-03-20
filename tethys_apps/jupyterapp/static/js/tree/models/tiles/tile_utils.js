"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var projections_1 = require("core/util/projections");
function geographic_to_meters(xLon, yLat) {
    return projections_1.wgs84_mercator.forward([xLon, yLat]);
}
exports.geographic_to_meters = geographic_to_meters;
function meters_to_geographic(mx, my) {
    return projections_1.wgs84_mercator.inverse([mx, my]);
}
exports.meters_to_geographic = meters_to_geographic;
function geographic_extent_to_meters(extent) {
    var g_xmin = extent[0], g_ymin = extent[1], g_xmax = extent[2], g_ymax = extent[3];
    var _a = geographic_to_meters(g_xmin, g_ymin), m_xmin = _a[0], m_ymin = _a[1];
    var _b = geographic_to_meters(g_xmax, g_ymax), m_xmax = _b[0], m_ymax = _b[1];
    return [m_xmin, m_ymin, m_xmax, m_ymax];
}
exports.geographic_extent_to_meters = geographic_extent_to_meters;
function meters_extent_to_geographic(extent) {
    var m_xmin = extent[0], m_ymin = extent[1], m_xmax = extent[2], m_ymax = extent[3];
    var _a = meters_to_geographic(m_xmin, m_ymin), g_xmin = _a[0], g_ymin = _a[1];
    var _b = meters_to_geographic(m_xmax, m_ymax), g_xmax = _b[0], g_ymax = _b[1];
    return [g_xmin, g_ymin, g_xmax, g_ymax];
}
exports.meters_extent_to_geographic = meters_extent_to_geographic;
