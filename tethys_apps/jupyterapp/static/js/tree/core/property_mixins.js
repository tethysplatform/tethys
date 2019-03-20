"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var p = require("./properties");
var object_1 = require("./util/object");
function _gen_mixin(mixin, prefix) {
    var result = {};
    for (var name_1 in mixin) {
        var prop = mixin[name_1];
        result[prefix + name_1] = prop;
    }
    return result;
}
var _line_mixin = {
    line_color: [p.ColorSpec, 'black'],
    line_width: [p.NumberSpec, 1],
    line_alpha: [p.NumberSpec, 1.0],
    line_join: [p.LineJoin, 'bevel'],
    line_cap: [p.LineCap, 'butt'],
    line_dash: [p.Array, []],
    line_dash_offset: [p.Number, 0],
};
exports.line = function (prefix) {
    if (prefix === void 0) { prefix = ""; }
    return _gen_mixin(_line_mixin, prefix);
};
var _fill_mixin = {
    fill_color: [p.ColorSpec, 'gray'],
    fill_alpha: [p.NumberSpec, 1.0],
};
exports.fill = function (prefix) {
    if (prefix === void 0) { prefix = ""; }
    return _gen_mixin(_fill_mixin, prefix);
};
var _text_mixin = {
    text_font: [p.Font, 'helvetica'],
    text_font_size: [p.FontSizeSpec, '12pt'],
    text_font_style: [p.FontStyle, 'normal'],
    text_color: [p.ColorSpec, '#444444'],
    text_alpha: [p.NumberSpec, 1.0],
    text_align: [p.TextAlign, 'left'],
    text_baseline: [p.TextBaseline, 'bottom'],
    text_line_height: [p.Number, 1.2],
};
exports.text = function (prefix) {
    if (prefix === void 0) { prefix = ""; }
    return _gen_mixin(_text_mixin, prefix);
};
function create(configs) {
    var result = {};
    for (var _i = 0, configs_1 = configs; _i < configs_1.length; _i++) {
        var config = configs_1[_i];
        var _a = config.split(":"), kind = _a[0], prefix = _a[1];
        var mixin = void 0;
        switch (kind) {
            case "line":
                mixin = exports.line;
                break;
            case "fill":
                mixin = exports.fill;
                break;
            case "text":
                mixin = exports.text;
                break;
            default:
                throw new Error("Unknown property mixin kind '" + kind + "'");
        }
        object_1.extend(result, mixin(prefix));
    }
    return result;
}
exports.create = create;
