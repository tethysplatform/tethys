"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function splice(array, start, k) {
    var items = [];
    for (var _i = 3; _i < arguments.length; _i++) {
        items[_i - 3] = arguments[_i];
    }
    var len = array.length;
    if (start < 0)
        start += len;
    if (start < 0)
        start = 0;
    else if (start > len)
        start = len;
    if (k == null || k > len - start)
        k = len - start;
    else if (k < 0)
        k = 0;
    var n = len - k + items.length;
    var result = new array.constructor(n);
    var i = 0;
    for (; i < start; i++) {
        result[i] = array[i];
    }
    for (var _a = 0, items_1 = items; _a < items_1.length; _a++) {
        var item = items_1[_a];
        result[i++] = item;
    }
    for (var j = start + k; j < len; j++) {
        result[i++] = array[j];
    }
    return result;
}
exports.splice = splice;
function insert(array, item, i) {
    return splice(array, i, 0, item);
}
exports.insert = insert;
function append(array, item) {
    return splice(array, array.length, 0, item);
}
exports.append = append;
function prepend(array, item) {
    return splice(array, 0, 0, item);
}
exports.prepend = prepend;
function indexOf(array, item) {
    for (var i = 0, n = array.length; i < n; i++) {
        if (array[i] === item)
            return i;
    }
    return -1;
}
exports.indexOf = indexOf;
function map(array, fn) {
    var n = array.length;
    var result = new array.constructor(n);
    for (var i = 0; i < n; i++) {
        result[i] = fn(array[i], i, array);
    }
    return result;
}
exports.map = map;
function min(array) {
    var value;
    var result = Infinity;
    for (var i = 0, length_1 = array.length; i < length_1; i++) {
        value = array[i];
        if (value < result) {
            result = value;
        }
    }
    return result;
}
exports.min = min;
function minBy(array, key) {
    if (array.length == 0)
        throw new Error("minBy() called with an empty array");
    var result = array[0];
    var resultComputed = key(result);
    for (var i = 1, length_2 = array.length; i < length_2; i++) {
        var value = array[i];
        var computed = key(value);
        if (computed < resultComputed) {
            result = value;
            resultComputed = computed;
        }
    }
    return result;
}
exports.minBy = minBy;
function max(array) {
    var value;
    var result = -Infinity;
    for (var i = 0, length_3 = array.length; i < length_3; i++) {
        value = array[i];
        if (value > result) {
            result = value;
        }
    }
    return result;
}
exports.max = max;
function maxBy(array, key) {
    if (array.length == 0)
        throw new Error("maxBy() called with an empty array");
    var result = array[0];
    var resultComputed = key(result);
    for (var i = 1, length_4 = array.length; i < length_4; i++) {
        var value = array[i];
        var computed = key(value);
        if (computed > resultComputed) {
            result = value;
            resultComputed = computed;
        }
    }
    return result;
}
exports.maxBy = maxBy;
function sum(array) {
    var result = 0;
    for (var i = 0, n = array.length; i < n; i++) {
        result += array[i];
    }
    return result;
}
exports.sum = sum;
