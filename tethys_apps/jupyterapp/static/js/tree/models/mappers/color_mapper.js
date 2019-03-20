"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var mapper_1 = require("./mapper");
var p = require("core/properties");
var color_1 = require("core/util/color");
var compat_1 = require("core/util/compat");
function _convert_color(color) {
    if (color[0] != "#")
        color = color_1.color2hex(color);
    if (color.length != 9)
        color = color + 'ff';
    return parseInt(color.slice(1), 16);
}
exports._convert_color = _convert_color;
function _convert_palette(palette) {
    var new_palette = new Uint32Array(palette.length);
    for (var i = 0, end = palette.length; i < end; i++)
        new_palette[i] = _convert_color(palette[i]);
    return new_palette;
}
exports._convert_palette = _convert_palette;
function _uint32_to_rgba(values) {
    if (compat_1.is_little_endian) {
        var view = new DataView(values.buffer);
        for (var i = 0, end = values.length; i < end; i++)
            view.setUint32(i * 4, values[i]);
    }
    return new Uint8Array(values.buffer);
}
exports._uint32_to_rgba = _uint32_to_rgba;
var ColorMapper = /** @class */ (function (_super) {
    tslib_1.__extends(ColorMapper, _super);
    function ColorMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    ColorMapper.initClass = function () {
        this.prototype.type = "ColorMapper";
        this.define({
            palette: [p.Any],
            nan_color: [p.Color, "gray"],
        });
    };
    ColorMapper.prototype.v_compute = function (xs) {
        var values = new Array(xs.length);
        this._v_compute(xs, values, this.palette, this._colors(function (c) { return c; }));
        return values;
    };
    Object.defineProperty(ColorMapper.prototype, "rgba_mapper", {
        get: function () {
            var self = this;
            var palette = _convert_palette(this.palette);
            var colors = this._colors(_convert_color);
            return {
                v_compute: function (xs) {
                    var values = new Uint32Array(xs.length);
                    self._v_compute(xs, values, palette, colors);
                    return _uint32_to_rgba(values);
                },
            };
        },
        enumerable: true,
        configurable: true
    });
    ColorMapper.prototype._colors = function (conv) {
        return { nan_color: conv(this.nan_color) };
    };
    return ColorMapper;
}(mapper_1.Mapper));
exports.ColorMapper = ColorMapper;
ColorMapper.initClass();
