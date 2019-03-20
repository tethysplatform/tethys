"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function concat(array0) {
    var arrays = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        arrays[_i - 1] = arguments[_i];
    }
    var n = array0.length;
    for (var _a = 0, arrays_1 = arrays; _a < arrays_1.length; _a++) {
        var array = arrays_1[_a];
        n += array.length;
    }
    var result = new array0.constructor(n);
    result.set(array0, 0);
    var i = array0.length;
    for (var _b = 0, arrays_2 = arrays; _b < arrays_2.length; _b++) {
        var array = arrays_2[_b];
        result.set(array, i);
        i += array.length;
    }
    return result;
}
exports.concat = concat;
