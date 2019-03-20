"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var continuous_ticker_1 = require("./continuous_ticker");
var p = require("core/properties");
var array_1 = require("core/util/array");
// Forces a number x into a specified range [min_val, max_val].
function clamp(x, min_val, max_val) {
    return Math.max(min_val, Math.min(max_val, x));
}
// A log function with an optional base.
function log(x, base) {
    if (base === void 0) { base = Math.E; }
    return Math.log(x) / Math.log(base);
}
var AdaptiveTicker = /** @class */ (function (_super) {
    tslib_1.__extends(AdaptiveTicker, _super);
    function AdaptiveTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    AdaptiveTicker.initClass = function () {
        this.prototype.type = "AdaptiveTicker";
        this.define({
            base: [p.Number, 10.0],
            mantissas: [p.Array, [1, 2, 5]],
            min_interval: [p.Number, 0.0],
            max_interval: [p.Number],
        });
    };
    // These arguments control the range of possible intervals.  The interval I
    // returned by get_interval() will be the one that most closely matches the
    // desired number of ticks, subject to the following constraints:
    // I = (M * B^N), where
    // M is a member of mantissas,
    // B is base,
    // and N is an integer;
    // and min_interval <= I <= max_interval.
    AdaptiveTicker.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        var prefix_mantissa = array_1.nth(this.mantissas, -1) / this.base;
        var suffix_mantissa = array_1.nth(this.mantissas, 0) * this.base;
        this.extended_mantissas = [prefix_mantissa].concat(this.mantissas, [suffix_mantissa]);
        this.base_factor = this.get_min_interval() === 0.0 ? 1.0 : this.get_min_interval();
    };
    AdaptiveTicker.prototype.get_interval = function (data_low, data_high, desired_n_ticks) {
        var data_range = data_high - data_low;
        var ideal_interval = this.get_ideal_interval(data_low, data_high, desired_n_ticks);
        var interval_exponent = Math.floor(log(ideal_interval / this.base_factor, this.base));
        var ideal_magnitude = Math.pow(this.base, interval_exponent) * this.base_factor;
        // An untested optimization.
        //   const ideal_mantissa = ideal_interval / ideal_magnitude
        //   index = sortedIndex(this.extended_mantissas, ideal_mantissa)
        //   candidate_mantissas = this.extended_mantissas[index..index + 1]
        var candidate_mantissas = this.extended_mantissas;
        var errors = candidate_mantissas.map(function (mantissa) {
            return Math.abs(desired_n_ticks - (data_range / (mantissa * ideal_magnitude)));
        });
        var best_mantissa = candidate_mantissas[array_1.argmin(errors)];
        var interval = best_mantissa * ideal_magnitude;
        return clamp(interval, this.get_min_interval(), this.get_max_interval());
    };
    return AdaptiveTicker;
}(continuous_ticker_1.ContinuousTicker));
exports.AdaptiveTicker = AdaptiveTicker;
AdaptiveTicker.initClass();
