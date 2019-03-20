"use strict";
//     Underscore.js 1.8.3
//     http://underscorejs.org
//     (c) 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
//     Underscore may be freely distributed under the MIT license.
Object.defineProperty(exports, "__esModule", { value: true });
var array_1 = require("./array");
var toString = Object.prototype.toString;
function isBoolean(obj) {
    return obj === true || obj === false || toString.call(obj) === '[object Boolean]';
}
exports.isBoolean = isBoolean;
function isNumber(obj) {
    return toString.call(obj) === "[object Number]";
}
exports.isNumber = isNumber;
function isInteger(obj) {
    return isNumber(obj) && isFinite(obj) && Math.floor(obj) === obj;
}
exports.isInteger = isInteger;
function isString(obj) {
    return toString.call(obj) === "[object String]";
}
exports.isString = isString;
function isStrictNaN(obj) {
    return isNumber(obj) && obj !== +obj;
}
exports.isStrictNaN = isStrictNaN;
function isFunction(obj) {
    return toString.call(obj) === "[object Function]";
}
exports.isFunction = isFunction;
function isArray(obj) {
    return Array.isArray(obj);
}
exports.isArray = isArray;
function isArrayOf(arr, predicate) {
    return array_1.all(arr, predicate);
}
exports.isArrayOf = isArrayOf;
function isArrayableOf(arr, predicate) {
    for (var i = 0, end = arr.length; i < end; i++) {
        if (!predicate(arr[i]))
            return false;
    }
    return true;
}
exports.isArrayableOf = isArrayableOf;
function isTypedArray(obj) {
    return obj != null && obj.buffer != null && obj.buffer instanceof ArrayBuffer;
}
exports.isTypedArray = isTypedArray;
function isObject(obj) {
    var tp = typeof obj;
    return tp === 'function' || tp === 'object' && !!obj;
}
exports.isObject = isObject;
function isPlainObject(obj) {
    return isObject(obj) && (obj.constructor == null || obj.constructor === Object);
}
exports.isPlainObject = isPlainObject;
