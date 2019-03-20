"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
function _cat_equals(a, b) {
    if (a.length != b.length)
        return false;
    for (var i = 0, end = a.length; i < end; i++) {
        if (a[i] !== b[i])
            return false;
    }
    return true;
}
exports._cat_equals = _cat_equals;
function cat_v_compute(data, factors, targets, values, start, end, extra_value) {
    var _loop_1 = function (i, N) {
        var d = data[i];
        var key = void 0;
        if (types_1.isString(d))
            key = factors.indexOf(d);
        else {
            if (start != null) {
                if (end != null)
                    d = d.slice(start, end);
                else
                    d = d.slice(start);
            }
            else if (end != null)
                d = d.slice(0, end);
            if (d.length == 1)
                key = factors.indexOf(d[0]);
            else
                key = array_1.findIndex(factors, function (x) { return _cat_equals(x, d); });
        }
        var value = void 0;
        if (key < 0 || key >= targets.length)
            value = extra_value;
        else
            value = targets[key];
        values[i] = value;
    };
    for (var i = 0, N = data.length; i < N; i++) {
        _loop_1(i, N);
    }
}
exports.cat_v_compute = cat_v_compute;
