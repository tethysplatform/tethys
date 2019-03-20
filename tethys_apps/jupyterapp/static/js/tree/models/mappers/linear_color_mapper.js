"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var continuous_color_mapper_1 = require("./continuous_color_mapper");
var arrayable_1 = require("core/util/arrayable");
var LinearColorMapper = /** @class */ (function (_super) {
    tslib_1.__extends(LinearColorMapper, _super);
    function LinearColorMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    LinearColorMapper.initClass = function () {
        this.prototype.type = "LinearColorMapper";
    };
    LinearColorMapper.prototype._v_compute = function (data, values, palette, colors) {
        var nan_color = colors.nan_color, low_color = colors.low_color, high_color = colors.high_color;
        var low = this.low != null ? this.low : arrayable_1.min(data);
        var high = this.high != null ? this.high : arrayable_1.max(data);
        var max_key = palette.length - 1;
        var norm_factor = 1 / (high - low);
        var normed_interval = 1 / palette.length;
        for (var i = 0, end = data.length; i < end; i++) {
            var d = data[i];
            if (isNaN(d)) {
                values[i] = nan_color;
                continue;
            }
            // This handles the edge case where d == high, since the code below maps
            // values exactly equal to high to palette.length, which is greater than
            // max_key
            if (d == high) {
                values[i] = palette[max_key];
                continue;
            }
            var normed_d = (d - low) * norm_factor;
            var key = Math.floor(normed_d / normed_interval);
            if (key < 0)
                values[i] = low_color != null ? low_color : palette[0];
            else if (key > max_key)
                values[i] = high_color != null ? high_color : palette[max_key];
            else
                values[i] = palette[key];
        }
    };
    return LinearColorMapper;
}(continuous_color_mapper_1.ContinuousColorMapper));
exports.LinearColorMapper = LinearColorMapper;
LinearColorMapper.initClass();
