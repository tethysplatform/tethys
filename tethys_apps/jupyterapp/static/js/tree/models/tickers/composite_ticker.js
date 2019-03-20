"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var continuous_ticker_1 = require("./continuous_ticker");
var p = require("core/properties");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var CompositeTicker = /** @class */ (function (_super) {
    tslib_1.__extends(CompositeTicker, _super);
    function CompositeTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    CompositeTicker.initClass = function () {
        this.prototype.type = "CompositeTicker";
        this.define({
            tickers: [p.Array, []],
        });
    };
    Object.defineProperty(CompositeTicker.prototype, "min_intervals", {
        // The tickers should be in order of increasing interval size; specifically,
        // if S comes before T, then it should be the case that
        // S.get_max_interval() < T.get_min_interval().
        // FIXME Enforce this automatically.
        get: function () {
            return this.tickers.map(function (ticker) { return ticker.get_min_interval(); });
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CompositeTicker.prototype, "max_intervals", {
        get: function () {
            return this.tickers.map(function (ticker) { return ticker.get_max_interval(); });
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CompositeTicker.prototype, "min_interval", {
        get: function () {
            return this.min_intervals[0];
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CompositeTicker.prototype, "max_interval", {
        get: function () {
            return this.max_intervals[0];
        },
        enumerable: true,
        configurable: true
    });
    CompositeTicker.prototype.get_best_ticker = function (data_low, data_high, desired_n_ticks) {
        var data_range = data_high - data_low;
        var ideal_interval = this.get_ideal_interval(data_low, data_high, desired_n_ticks);
        var ticker_ndxs = [
            array_1.sortedIndex(this.min_intervals, ideal_interval) - 1,
            array_1.sortedIndex(this.max_intervals, ideal_interval),
        ];
        var intervals = [
            this.min_intervals[ticker_ndxs[0]],
            this.max_intervals[ticker_ndxs[1]],
        ];
        var errors = intervals.map(function (interval) {
            return Math.abs(desired_n_ticks - (data_range / interval));
        });
        var best_ticker;
        if (object_1.isEmpty(errors.filter(function (e) { return !isNaN(e); }))) {
            // this can happen if the data isn't loaded yet, we just default to the first scale
            best_ticker = this.tickers[0];
        }
        else {
            var best_index = array_1.argmin(errors);
            var best_ticker_ndx = ticker_ndxs[best_index];
            best_ticker = this.tickers[best_ticker_ndx];
        }
        return best_ticker;
    };
    CompositeTicker.prototype.get_interval = function (data_low, data_high, desired_n_ticks) {
        var best_ticker = this.get_best_ticker(data_low, data_high, desired_n_ticks);
        return best_ticker.get_interval(data_low, data_high, desired_n_ticks);
    };
    CompositeTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, cross_loc, desired_n_ticks) {
        var best_ticker = this.get_best_ticker(data_low, data_high, desired_n_ticks);
        return best_ticker.get_ticks_no_defaults(data_low, data_high, cross_loc, desired_n_ticks);
    };
    return CompositeTicker;
}(continuous_ticker_1.ContinuousTicker));
exports.CompositeTicker = CompositeTicker;
CompositeTicker.initClass();
