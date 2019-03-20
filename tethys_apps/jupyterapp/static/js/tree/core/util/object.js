"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var array_1 = require("./array");
exports.keys = Object.keys;
function values(object) {
    var keys = Object.keys(object);
    var length = keys.length;
    var values = new Array(length);
    for (var i = 0; i < length; i++) {
        values[i] = object[keys[i]];
    }
    return values;
}
exports.values = values;
function extend(dest, src) {
    return tslib_1.__assign(dest, src);
}
exports.extend = extend;
function clone(obj) {
    return extend({}, obj); // XXX: can't use {...obj} due to https://github.com/Microsoft/TypeScript/issues/14409
}
exports.clone = clone;
function merge(obj1, obj2) {
    /*
     * Returns an object with the array values for obj1 and obj2 unioned by key.
     */
    var result = Object.create(Object.prototype);
    var keys = array_1.concat([Object.keys(obj1), Object.keys(obj2)]);
    for (var _i = 0, keys_1 = keys; _i < keys_1.length; _i++) {
        var key = keys_1[_i];
        var arr1 = obj1.hasOwnProperty(key) ? obj1[key] : [];
        var arr2 = obj2.hasOwnProperty(key) ? obj2[key] : [];
        result[key] = array_1.union(arr1, arr2);
    }
    return result;
}
exports.merge = merge;
function size(obj) {
    return Object.keys(obj).length;
}
exports.size = size;
function isEmpty(obj) {
    return size(obj) === 0;
}
exports.isEmpty = isEmpty;
