"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("core/util/types");
function isValue(obj) {
    return types_1.isObject(obj) && "value" in obj;
}
exports.isValue = isValue;
function isField(obj) {
    return types_1.isObject(obj) && "field" in obj;
}
exports.isField = isField;
