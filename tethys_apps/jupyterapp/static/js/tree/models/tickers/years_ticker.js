"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var basic_ticker_1 = require("./basic_ticker");
var single_interval_ticker_1 = require("./single_interval_ticker");
var util_1 = require("./util");
var YearsTicker = /** @class */ (function (_super) {
    tslib_1.__extends(YearsTicker, _super);
    function YearsTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    YearsTicker.initClass = function () {
        this.prototype.type = "YearsTicker";
    };
    YearsTicker.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.interval = util_1.ONE_YEAR;
        this.basic_ticker = new basic_ticker_1.BasicTicker({ num_minor_ticks: 0 });
    };
    YearsTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, cross_loc, desired_n_ticks) {
        var start_year = util_1.last_year_no_later_than(new Date(data_low)).getUTCFullYear();
        var end_year = util_1.last_year_no_later_than(new Date(data_high)).getUTCFullYear();
        var years = this.basic_ticker.get_ticks_no_defaults(start_year, end_year, cross_loc, desired_n_ticks).major;
        var all_ticks = years.map(function (year) { return Date.UTC(year, 0, 1); });
        var ticks_in_range = all_ticks.filter(function (tick) { return data_low <= tick && tick <= data_high; });
        return {
            major: ticks_in_range,
            minor: [],
        };
    };
    return YearsTicker;
}(single_interval_ticker_1.SingleIntervalTicker));
exports.YearsTicker = YearsTicker;
YearsTicker.initClass();
