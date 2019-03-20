"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var single_interval_ticker_1 = require("./single_interval_ticker");
var util_1 = require("./util");
var p = require("core/properties");
var array_1 = require("core/util/array");
// Given a start and end time in millis, returns the shortest array of
// consecutive months (as Dates) that surrounds both times.
function date_range_by_month(start_time, end_time) {
    var start_date = util_1.last_month_no_later_than(new Date(start_time));
    var end_date = util_1.last_month_no_later_than(new Date(end_time));
    // XXX This is not a reliable technique in general, but it should be
    // safe when the day of the month is 1.  (The problem case is this:
    // Mar 31 -> Apr 31, which becomes May 1.)
    end_date.setUTCMonth(end_date.getUTCMonth() + 1);
    var dates = [];
    var date = start_date;
    while (true) {
        dates.push(util_1.copy_date(date));
        date.setUTCMonth(date.getUTCMonth() + 1);
        if (date > end_date)
            break;
    }
    return dates;
}
var DaysTicker = /** @class */ (function (_super) {
    tslib_1.__extends(DaysTicker, _super);
    function DaysTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    DaysTicker.initClass = function () {
        this.prototype.type = "DaysTicker";
        this.define({
            days: [p.Array, []],
        });
        this.override({
            num_minor_ticks: 0,
        });
    };
    DaysTicker.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        var days = this.days;
        if (days.length > 1)
            this.interval = (days[1] - days[0]) * util_1.ONE_DAY;
        else
            this.interval = 31 * util_1.ONE_DAY;
    };
    DaysTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, _cross_loc, _desired_n_ticks) {
        var month_dates = date_range_by_month(data_low, data_high);
        var days = this.days;
        var days_of_month = function (month_date, interval) {
            var current_month = month_date.getUTCMonth();
            var dates = [];
            for (var _i = 0, days_1 = days; _i < days_1.length; _i++) {
                var day = days_1[_i];
                var day_date = util_1.copy_date(month_date);
                day_date.setUTCDate(day);
                // We can't use all of the values in this.days, because they may not
                // fall within the current month.  In fact, if, e.g., our month is 28 days
                // and we're marking every third day, we don't want day 28 to show up
                // because it'll be right next to the 1st of the next month.  So we
                // make sure we have a bit of room before we include a day.
                // TODO (bev) The above description does not exactly work because JS Date
                // is broken and will happily consider "Feb 28 + 3*ONE_DAY" to have month "2"
                var future_date = new Date(day_date.getTime() + (interval / 2));
                if (future_date.getUTCMonth() == current_month)
                    dates.push(day_date);
            }
            return dates;
        };
        var interval = this.interval;
        var day_dates = array_1.concat(month_dates.map(function (date) { return days_of_month(date, interval); }));
        var all_ticks = day_dates.map(function (day_date) { return day_date.getTime(); });
        var ticks_in_range = all_ticks.filter(function (tick) { return data_low <= tick && tick <= data_high; });
        return {
            major: ticks_in_range,
            minor: [],
        };
    };
    return DaysTicker;
}(single_interval_ticker_1.SingleIntervalTicker));
exports.DaysTicker = DaysTicker;
DaysTicker.initClass();
