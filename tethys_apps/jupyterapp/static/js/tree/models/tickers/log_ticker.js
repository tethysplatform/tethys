"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var adaptive_ticker_1 = require("./adaptive_ticker");
var array_1 = require("core/util/array");
var LogTicker = /** @class */ (function (_super) {
    tslib_1.__extends(LogTicker, _super);
    function LogTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    LogTicker.initClass = function () {
        this.prototype.type = "LogTicker";
        this.override({
            mantissas: [1, 5],
        });
    };
    LogTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, _cross_loc, desired_n_ticks) {
        var num_minor_ticks = this.num_minor_ticks;
        var minor_ticks = [];
        var base = this.base;
        var log_low = Math.log(data_low) / Math.log(base);
        var log_high = Math.log(data_high) / Math.log(base);
        var log_interval = log_high - log_low;
        var ticks;
        if (!isFinite(log_interval)) {
            ticks = [];
        }
        else if (log_interval < 2) { // treat as linear ticker
            var interval_1 = this.get_interval(data_low, data_high, desired_n_ticks);
            var start_factor = Math.floor(data_low / interval_1);
            var end_factor = Math.ceil(data_high / interval_1);
            ticks = array_1.range(start_factor, end_factor + 1)
                .filter(function (factor) { return factor != 0; })
                .map(function (factor) { return factor * interval_1; })
                .filter(function (tick) { return data_low <= tick && tick <= data_high; });
            if (num_minor_ticks > 0 && ticks.length > 0) {
                var minor_interval_1 = interval_1 / num_minor_ticks;
                var minor_offsets = array_1.range(0, num_minor_ticks).map(function (i) { return i * minor_interval_1; });
                for (var _i = 0, _a = minor_offsets.slice(1); _i < _a.length; _i++) {
                    var x = _a[_i];
                    minor_ticks.push(ticks[0] - x);
                }
                for (var _b = 0, ticks_1 = ticks; _b < ticks_1.length; _b++) {
                    var tick = ticks_1[_b];
                    for (var _c = 0, minor_offsets_1 = minor_offsets; _c < minor_offsets_1.length; _c++) {
                        var x = minor_offsets_1[_c];
                        minor_ticks.push(tick + x);
                    }
                }
            }
        }
        else {
            var startlog = Math.ceil(log_low * 0.999999);
            var endlog = Math.floor(log_high * 1.000001);
            var interval = Math.ceil((endlog - startlog) / 9.0);
            ticks = array_1.range(startlog - 1, endlog + 1, interval)
                .map(function (i) { return Math.pow(base, i); });
            if (num_minor_ticks > 0 && ticks.length > 0) {
                var minor_interval_2 = Math.pow(base, interval) / num_minor_ticks;
                var minor_offsets = array_1.range(1, num_minor_ticks + 1).map(function (i) { return i * minor_interval_2; });
                for (var _d = 0, minor_offsets_2 = minor_offsets; _d < minor_offsets_2.length; _d++) {
                    var x = minor_offsets_2[_d];
                    minor_ticks.push(ticks[0] / x);
                }
                minor_ticks.push(ticks[0]);
                for (var _e = 0, ticks_2 = ticks; _e < ticks_2.length; _e++) {
                    var tick = ticks_2[_e];
                    for (var _f = 0, minor_offsets_3 = minor_offsets; _f < minor_offsets_3.length; _f++) {
                        var x = minor_offsets_3[_f];
                        minor_ticks.push(tick * x);
                    }
                }
            }
        }
        return {
            major: ticks.filter(function (tick) { return data_low <= tick && tick <= data_high; }),
            minor: minor_ticks.filter(function (tick) { return data_low <= tick && tick <= data_high; }),
        };
    };
    return LogTicker;
}(adaptive_ticker_1.AdaptiveTicker));
exports.LogTicker = LogTicker;
LogTicker.initClass();
