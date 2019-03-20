"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var single_interval_ticker_1 = require("./single_interval_ticker");
var util_1 = require("./util");
var p = require("core/properties");
var array_1 = require("core/util/array");
// Given a start and end time in millis, returns the shortest array of
// consecutive years (as Dates) that surrounds both times.
function date_range_by_year(start_time, end_time) {
    var start_date = util_1.last_year_no_later_than(new Date(start_time));
    var end_date = util_1.last_year_no_later_than(new Date(end_time));
    end_date.setUTCFullYear(end_date.getUTCFullYear() + 1);
    var dates = [];
    var date = start_date;
    while (true) {
        dates.push(util_1.copy_date(date));
        date.setUTCFullYear(date.getUTCFullYear() + 1);
        if (date > end_date)
            break;
    }
    return dates;
}
var MonthsTicker = /** @class */ (function (_super) {
    tslib_1.__extends(MonthsTicker, _super);
    function MonthsTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    MonthsTicker.initClass = function () {
        this.prototype.type = "MonthsTicker";
        this.define({
            months: [p.Array, []],
        });
    };
    MonthsTicker.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        var months = this.months;
        if (months.length > 1)
            this.interval = (months[1] - months[0]) * util_1.ONE_MONTH;
        else
            this.interval = 12 * util_1.ONE_MONTH;
    };
    MonthsTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, _cross_loc, _desired_n_ticks) {
        var year_dates = date_range_by_year(data_low, data_high);
        var months = this.months;
        var months_of_year = function (year_date) {
            return months.map(function (month) {
                var month_date = util_1.copy_date(year_date);
                month_date.setUTCMonth(month);
                return month_date;
            });
        };
        var month_dates = array_1.concat(year_dates.map(months_of_year));
        var all_ticks = month_dates.map(function (month_date) { return month_date.getTime(); });
        var ticks_in_range = all_ticks.filter(function (tick) { return data_low <= tick && tick <= data_high; });
        return {
            major: ticks_in_range,
            minor: [],
        };
    };
    return MonthsTicker;
}(single_interval_ticker_1.SingleIntervalTicker));
exports.MonthsTicker = MonthsTicker;
MonthsTicker.initClass();
