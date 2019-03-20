"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var array_1 = require("./util/array");
var selection_1 = require("../models/selections/selection");
function point_in_poly(x, y, px, py) {
    var inside = false;
    var x1 = px[px.length - 1];
    var y1 = py[py.length - 1];
    for (var i = 0; i < px.length; i++) {
        var x2 = px[i];
        var y2 = py[i];
        if ((y1 < y) != (y2 < y)) {
            if (x1 + (y - y1) / (y2 - y1) * (x2 - x1) < x)
                inside = !inside;
        }
        x1 = x2;
        y1 = y2;
    }
    return inside;
}
exports.point_in_poly = point_in_poly;
function point_in_ellipse(x, y, angle, b, a, x0, y0) {
    var A = (Math.pow((Math.cos(angle) / a), 2) + Math.pow((Math.sin(angle) / b), 2));
    var B = 2 * Math.cos(angle) * Math.sin(angle) * (Math.pow((1 / a), 2) - Math.pow((1 / b), 2));
    var C = (Math.pow((Math.cos(angle) / b), 2) + Math.pow((Math.sin(angle) / a), 2));
    var eqn = A * Math.pow((x - x0), 2) + B * (x - x0) * (y - y0) + C * Math.pow((y - y0), 2);
    var inside = eqn <= 1;
    return inside;
}
exports.point_in_ellipse = point_in_ellipse;
function create_empty_hit_test_result() {
    return new selection_1.Selection();
}
exports.create_empty_hit_test_result = create_empty_hit_test_result;
function create_hit_test_result_from_hits(hits) {
    var result = new selection_1.Selection();
    result.indices = array_1.sortBy(hits, function (_a) {
        var _i = _a[0], dist = _a[1];
        return dist;
    }).map(function (_a) {
        var i = _a[0], _dist = _a[1];
        return i;
    });
    return result;
}
exports.create_hit_test_result_from_hits = create_hit_test_result_from_hits;
function validate_bbox_coords(_a, _b) {
    var x0 = _a[0], x1 = _a[1];
    var y0 = _b[0], y1 = _b[1];
    var _c, _d;
    // spatial index (flatbush) expects x0, y0 to be min, x1, y1 max
    if (x0 > x1)
        _c = [x1, x0], x0 = _c[0], x1 = _c[1];
    if (y0 > y1)
        _d = [y1, y0], y0 = _d[0], y1 = _d[1];
    return { minX: x0, minY: y0, maxX: x1, maxY: y1 };
}
exports.validate_bbox_coords = validate_bbox_coords;
function sqr(x) {
    return x * x;
}
function dist_2_pts(p0, p1) {
    return sqr(p0.x - p1.x) + sqr(p0.y - p1.y);
}
exports.dist_2_pts = dist_2_pts;
function dist_to_segment_squared(p, v, w) {
    var l2 = dist_2_pts(v, w);
    if (l2 == 0)
        return dist_2_pts(p, v);
    var t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
    if (t < 0)
        return dist_2_pts(p, v);
    if (t > 1)
        return dist_2_pts(p, w);
    var q = { x: v.x + t * (w.x - v.x), y: v.y + t * (w.y - v.y) };
    return dist_2_pts(p, q);
}
exports.dist_to_segment_squared = dist_to_segment_squared;
function dist_to_segment(p, v, w) {
    return Math.sqrt(dist_to_segment_squared(p, v, w));
}
exports.dist_to_segment = dist_to_segment;
function check_2_segments_intersect(l0_x0, l0_y0, l0_x1, l0_y1, l1_x0, l1_y0, l1_x1, l1_y1) {
    /*
     *  Check if 2 segments (l0 and l1) intersect. Returns a structure with
     *  the following attributes:
     *   * hit (boolean): whether the 2 segments intersect
     *   * x (float): x coordinate of the intersection point
     *   * y (float): y coordinate of the intersection point
     */
    var den = ((l1_y1 - l1_y0) * (l0_x1 - l0_x0)) - ((l1_x1 - l1_x0) * (l0_y1 - l0_y0));
    if (den == 0) {
        return { hit: false, x: null, y: null };
    }
    else {
        var a = l0_y0 - l1_y0;
        var b = l0_x0 - l1_x0;
        var num1 = ((l1_x1 - l1_x0) * a) - ((l1_y1 - l1_y0) * b);
        var num2 = ((l0_x1 - l0_x0) * a) - ((l0_y1 - l0_y0) * b);
        a = num1 / den;
        b = num2 / den;
        var x = l0_x0 + (a * (l0_x1 - l0_x0));
        var y = l0_y0 + (a * (l0_y1 - l0_y0));
        return {
            hit: (a > 0 && a < 1) && (b > 0 && b < 1),
            x: x,
            y: y,
        };
    }
}
exports.check_2_segments_intersect = check_2_segments_intersect;
