"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var continuous_color_mapper_1 = require("./continuous_color_mapper");
var arrayable_1 = require("core/util/arrayable");
// Math.log1p() is not supported by any version of IE, so let's use a polyfill based on
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/log1p.
var log1p = Math.log1p != null ? Math.log1p : function (x) { return Math.log(1 + x); };
var LogColorMapper = /** @class */ (function (_super) {
    tslib_1.__extends(LogColorMapper, _super);
    function LogColorMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    LogColorMapper.initClass = function () {
        this.prototype.type = "LogColorMapper";
    };
    LogColorMapper.prototype._v_compute = function (data, values, palette, colors) {
        var nan_color = colors.nan_color, low_color = colors.low_color, high_color = colors.high_color;
        var n = palette.length;
        var low = this.low != null ? this.low : arrayable_1.min(data);
        var high = this.high != null ? this.high : arrayable_1.max(data);
        var scale = n / (log1p(high) - log1p(low)); // subtract the low offset
        var max_key = palette.length - 1;
        for (var i = 0, end = data.length; i < end; i++) {
            var d = data[i];
            // Check NaN
            if (isNaN(d)) {
                values[i] = nan_color;
                continue;
            }
            if (d > high) {
                values[i] = high_color != null ? high_color : palette[max_key];
                continue;
            }
            // This handles the edge case where d == high, since the code below maps
            // values exactly equal to high to palette.length, which is greater than
            // max_key
            if (d == high) {
                values[i] = palette[max_key];
                continue;
            }
            if (d < low) {
                values[i] = low_color != null ? low_color : palette[0];
                continue;
            }
            // Get the key
            var log = log1p(d) - log1p(low); // subtract the low offset
            var key = Math.floor(log * scale);
            // Deal with upper bound
            if (key > max_key)
                key = max_key;
            values[i] = palette[key];
        }
    };
    return LogColorMapper;
}(continuous_color_mapper_1.ContinuousColorMapper));
exports.LogColorMapper = LogColorMapper;
LogColorMapper.initClass();
