"use strict";
//     Underscore.js 1.8.3
//     http://underscorejs.org
//     (c) 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
//     Underscore may be freely distributed under the MIT license.
Object.defineProperty(exports, "__esModule", { value: true });
var math_1 = require("./math");
var assert_1 = require("./assert");
var arrayable_1 = require("./arrayable");
exports.min = arrayable_1.min;
exports.minBy = arrayable_1.minBy;
exports.max = arrayable_1.max;
exports.maxBy = arrayable_1.maxBy;
exports.sum = arrayable_1.sum;
var slice = Array.prototype.slice;
function head(array) {
    return array[0];
}
exports.head = head;
function tail(array) {
    return array[array.length - 1];
}
exports.tail = tail;
function last(array) {
    return array[array.length - 1];
}
exports.last = last;
function copy(array) {
    return slice.call(array);
}
exports.copy = copy;
function concat(arrays) {
    var _a;
    return (_a = []).concat.apply(_a, arrays);
}
exports.concat = concat;
function includes(array, value) {
    return array.indexOf(value) !== -1;
}
exports.includes = includes;
exports.contains = includes;
function nth(array, index) {
    return array[index >= 0 ? index : array.length + index];
}
exports.nth = nth;
function zip(As, Bs) {
    var n = Math.min(As.length, Bs.length);
    var ABs = new Array(n);
    for (var i = 0; i < n; i++) {
        ABs[i] = [As[i], Bs[i]];
    }
    return ABs;
}
exports.zip = zip;
function unzip(ABs) {
    var _a;
    var n = ABs.length;
    var As = new Array(n);
    var Bs = new Array(n);
    for (var i = 0; i < n; i++) {
        _a = ABs[i], As[i] = _a[0], Bs[i] = _a[1];
    }
    return [As, Bs];
}
exports.unzip = unzip;
function range(start, stop, step) {
    if (step === void 0) { step = 1; }
    assert_1.assert(step > 0, "'step' must be a positive number");
    if (stop == null) {
        stop = start;
        start = 0;
    }
    var max = Math.max, ceil = Math.ceil, abs = Math.abs;
    var delta = start <= stop ? step : -step;
    var length = max(ceil(abs(stop - start) / step), 0);
    var range = Array(length);
    for (var i = 0; i < length; i++, start += delta) {
        range[i] = start;
    }
    return range;
}
exports.range = range;
function linspace(start, stop, num) {
    if (num === void 0) { num = 100; }
    var step = (stop - start) / (num - 1);
    var array = new Array(num);
    for (var i = 0; i < num; i++) {
        array[i] = start + step * i;
    }
    return array;
}
exports.linspace = linspace;
function transpose(array) {
    var rows = array.length;
    var cols = array[0].length;
    var transposed = [];
    for (var j = 0; j < cols; j++) {
        transposed[j] = [];
        for (var i = 0; i < rows; i++) {
            transposed[j][i] = array[i][j];
        }
    }
    return transposed;
}
exports.transpose = transpose;
function cumsum(array) {
    var result = [];
    array.reduce(function (a, b, i) { return result[i] = a + b; }, 0);
    return result;
}
exports.cumsum = cumsum;
function argmin(array) {
    return arrayable_1.minBy(range(array.length), function (i) { return array[i]; });
}
exports.argmin = argmin;
function argmax(array) {
    return arrayable_1.maxBy(range(array.length), function (i) { return array[i]; });
}
exports.argmax = argmax;
function all(array, predicate) {
    for (var _i = 0, array_1 = array; _i < array_1.length; _i++) {
        var item = array_1[_i];
        if (!predicate(item))
            return false;
    }
    return true;
}
exports.all = all;
function any(array, predicate) {
    for (var _i = 0, array_2 = array; _i < array_2.length; _i++) {
        var item = array_2[_i];
        if (predicate(item))
            return true;
    }
    return false;
}
exports.any = any;
function findIndexFactory(dir) {
    return function (array, predicate) {
        var length = array.length;
        var index = dir > 0 ? 0 : length - 1;
        for (; index >= 0 && index < length; index += dir) {
            if (predicate(array[index]))
                return index;
        }
        return -1;
    };
}
exports.findIndex = findIndexFactory(1);
exports.findLastIndex = findIndexFactory(-1);
function find(array, predicate) {
    var index = exports.findIndex(array, predicate);
    return index == -1 ? undefined : array[index];
}
exports.find = find;
function findLast(array, predicate) {
    var index = exports.findLastIndex(array, predicate);
    return index == -1 ? undefined : array[index];
}
exports.findLast = findLast;
function sortedIndex(array, value) {
    var low = 0;
    var high = array.length;
    while (low < high) {
        var mid = Math.floor((low + high) / 2);
        if (array[mid] < value)
            low = mid + 1;
        else
            high = mid;
    }
    return low;
}
exports.sortedIndex = sortedIndex;
function sortBy(array, key) {
    var tmp = array.map(function (value, index) {
        return { value: value, index: index, key: key(value) };
    });
    tmp.sort(function (left, right) {
        var a = left.key;
        var b = right.key;
        if (a !== b) {
            if (a > b || a === undefined)
                return 1;
            if (a < b || b === undefined)
                return -1;
        }
        return left.index - right.index;
    });
    return tmp.map(function (item) { return item.value; });
}
exports.sortBy = sortBy;
function uniq(array) {
    var result = [];
    for (var _i = 0, array_3 = array; _i < array_3.length; _i++) {
        var value = array_3[_i];
        if (!includes(result, value)) {
            result.push(value);
        }
    }
    return result;
}
exports.uniq = uniq;
function uniqBy(array, key) {
    var result = [];
    var seen = [];
    for (var _i = 0, array_4 = array; _i < array_4.length; _i++) {
        var value = array_4[_i];
        var computed = key(value);
        if (!includes(seen, computed)) {
            seen.push(computed);
            result.push(value);
        }
    }
    return result;
}
exports.uniqBy = uniqBy;
function union() {
    var arrays = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        arrays[_i] = arguments[_i];
    }
    return uniq(concat(arrays));
}
exports.union = union;
function intersection(array) {
    var arrays = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        arrays[_i - 1] = arguments[_i];
    }
    var result = [];
    top: for (var _a = 0, array_5 = array; _a < array_5.length; _a++) {
        var item = array_5[_a];
        if (includes(result, item))
            continue;
        for (var _b = 0, arrays_1 = arrays; _b < arrays_1.length; _b++) {
            var other = arrays_1[_b];
            if (!includes(other, item))
                continue top;
        }
        result.push(item);
    }
    return result;
}
exports.intersection = intersection;
function difference(array) {
    var arrays = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        arrays[_i - 1] = arguments[_i];
    }
    var rest = concat(arrays);
    return array.filter(function (value) { return !includes(rest, value); });
}
exports.difference = difference;
function removeBy(array, key) {
    for (var i = 0; i < array.length;) {
        if (key(array[i]))
            array.splice(i, 1);
        else
            i++;
    }
}
exports.removeBy = removeBy;
// Shuffle a collection, using the modern version of the
// [Fisher-Yates shuffle](http://en.wikipedia.org/wiki/Fisher–Yates_shuffle).
function shuffle(array) {
    var length = array.length;
    var shuffled = new Array(length);
    for (var i = 0; i < length; i++) {
        var rand = math_1.randomIn(0, i);
        if (rand !== i)
            shuffled[i] = shuffled[rand];
        shuffled[rand] = array[i];
    }
    return shuffled;
}
exports.shuffle = shuffle;
function pairwise(array, fn) {
    var n = array.length;
    var result = new Array(n - 1);
    for (var i = 0; i < n - 1; i++) {
        result[i] = fn(array[i], array[i + 1]);
    }
    return result;
}
exports.pairwise = pairwise;
function reversed(array) {
    var n = array.length;
    var result = new Array(n);
    for (var i = 0; i < n; i++) {
        result[n - i - 1] = array[i];
    }
    return result;
}
exports.reversed = reversed;
function repeat(value, n) {
    var result = new Array(n);
    for (var i = 0; i < n; i++) {
        result[i] = value;
    }
    return result;
}
exports.repeat = repeat;
