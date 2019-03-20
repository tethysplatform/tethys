"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function angle_norm(angle) {
    while (angle < 0) {
        angle += 2 * Math.PI;
    }
    while (angle > 2 * Math.PI) {
        angle -= 2 * Math.PI;
    }
    return angle;
}
exports.angle_norm = angle_norm;
function angle_dist(lhs, rhs) {
    return Math.abs(angle_norm(lhs - rhs));
}
exports.angle_dist = angle_dist;
function angle_between(mid, lhs, rhs, direction) {
    var norm_mid = angle_norm(mid);
    var d = angle_dist(lhs, rhs);
    var cond = angle_dist(lhs, norm_mid) <= d && angle_dist(norm_mid, rhs) <= d;
    if (direction == 1 /* anticlock */)
        return !cond;
    else
        return cond;
}
exports.angle_between = angle_between;
function random() {
    return Math.random();
}
exports.random = random;
function randomIn(min, max) {
    if (max == null) {
        max = min;
        min = 0;
    }
    return min + Math.floor(Math.random() * (max - min + 1));
}
exports.randomIn = randomIn;
function atan2(start, end) {
    /*
     * Calculate the angle between a line containing start and end points (composed
     * of [x, y] arrays) and the positive x-axis.
     */
    return Math.atan2(end[1] - start[1], end[0] - start[0]);
}
exports.atan2 = atan2;
// http://www2.econ.osaka-u.ac.jp/~tanizaki/class/2013/econome3/13.pdf (Page 432)
function rnorm(mu, sigma) {
    // Generate a random normal with a mean of 0 and a sigma of 1
    var r1;
    var r2;
    while (true) {
        r1 = random();
        r2 = random();
        r2 = (2 * r2 - 1) * Math.sqrt(2 * (1 / Math.E));
        if (-4 * r1 * r1 * Math.log(r1) >= r2 * r2)
            break;
    }
    var rn = r2 / r1;
    // Transform the standard normal to meet the characteristics that we want (mu, sigma)
    rn = mu + sigma * rn;
    return rn;
}
exports.rnorm = rnorm;
function clamp(val, min, max) {
    if (val > max)
        return max;
    if (val < min)
        return min;
    return val;
}
exports.clamp = clamp;
