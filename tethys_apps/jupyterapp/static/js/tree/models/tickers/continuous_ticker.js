"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var ticker_1 = require("./ticker");
var p = require("core/properties");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var ContinuousTicker = /** @class */ (function (_super) {
    tslib_1.__extends(ContinuousTicker, _super);
    function ContinuousTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    ContinuousTicker.initClass = function () {
        this.prototype.type = "ContinuousTicker";
        this.define({
            num_minor_ticks: [p.Number, 5],
            desired_num_ticks: [p.Number, 6],
        });
    };
    ContinuousTicker.prototype.get_ticks = function (data_low, data_high, _range, cross_loc, _) {
        return this.get_ticks_no_defaults(data_low, data_high, cross_loc, this.desired_num_ticks);
    };
    // The version of get_ticks() that does the work (and the version that
    // should be overridden in subclasses).
    ContinuousTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, _cross_loc, desired_n_ticks) {
        var interval = this.get_interval(data_low, data_high, desired_n_ticks);
        var start_factor = Math.floor(data_low / interval);
        var end_factor = Math.ceil(data_high / interval);
        var factors;
        if (types_1.isStrictNaN(start_factor) || types_1.isStrictNaN(end_factor))
            factors = [];
        else
            factors = array_1.range(start_factor, end_factor + 1);
        var ticks = factors.map(function (factor) { return factor * interval; })
            .filter(function (tick) { return data_low <= tick && tick <= data_high; });
        var num_minor_ticks = this.num_minor_ticks;
        var minor_ticks = [];
        if (num_minor_ticks > 0 && ticks.length > 0) {
            var minor_interval_1 = interval / num_minor_ticks;
            var minor_offsets = array_1.range(0, num_minor_ticks).map(function (i) { return i * minor_interval_1; });
            for (var _i = 0, _a = minor_offsets.slice(1); _i < _a.length; _i++) {
                var x = _a[_i];
                var mt = ticks[0] - x;
                if (data_low <= mt && mt <= data_high) {
                    minor_ticks.push(mt);
                }
            }
            for (var _b = 0, ticks_1 = ticks; _b < ticks_1.length; _b++) {
                var tick = ticks_1[_b];
                for (var _c = 0, minor_offsets_1 = minor_offsets; _c < minor_offsets_1.length; _c++) {
                    var x = minor_offsets_1[_c];
                    var mt = tick + x;
                    if (data_low <= mt && mt <= data_high) {
                        minor_ticks.push(mt);
                    }
                }
            }
        }
        return {
            major: ticks,
            minor: minor_ticks,
        };
    };
    // Returns the smallest interval that can be returned by get_interval().
    ContinuousTicker.prototype.get_min_interval = function () {
        return this.min_interval;
    };
    // Returns the largest interval that can be returned by get_interval().
    ContinuousTicker.prototype.get_max_interval = function () {
        return this.max_interval != null ? this.max_interval : Infinity;
    };
    // Returns the interval size that would produce exactly the number of
    // desired ticks.  (In general we won't use exactly this interval, because
    // we want the ticks to be round numbers.)
    ContinuousTicker.prototype.get_ideal_interval = function (data_low, data_high, desired_n_ticks) {
        var data_range = data_high - data_low;
        return data_range / desired_n_ticks;
    };
    return ContinuousTicker;
}(ticker_1.Ticker));
exports.ContinuousTicker = ContinuousTicker;
ContinuousTicker.initClass();
