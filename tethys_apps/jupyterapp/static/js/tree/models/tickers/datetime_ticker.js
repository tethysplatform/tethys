"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var array_1 = require("core/util/array");
var adaptive_ticker_1 = require("./adaptive_ticker");
var composite_ticker_1 = require("./composite_ticker");
var days_ticker_1 = require("./days_ticker");
var months_ticker_1 = require("./months_ticker");
var years_ticker_1 = require("./years_ticker");
var util_1 = require("./util");
var DatetimeTicker = /** @class */ (function (_super) {
    tslib_1.__extends(DatetimeTicker, _super);
    function DatetimeTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    DatetimeTicker.initClass = function () {
        this.prototype.type = "DatetimeTicker";
        this.override({
            num_minor_ticks: 0,
            tickers: function () { return [
                // Sub-second.
                new adaptive_ticker_1.AdaptiveTicker({
                    mantissas: [1, 2, 5],
                    base: 10,
                    min_interval: 0,
                    max_interval: 500 * util_1.ONE_MILLI,
                    num_minor_ticks: 0,
                }),
                // Seconds, minutes.
                new adaptive_ticker_1.AdaptiveTicker({
                    mantissas: [1, 2, 5, 10, 15, 20, 30],
                    base: 60,
                    min_interval: util_1.ONE_SECOND,
                    max_interval: 30 * util_1.ONE_MINUTE,
                    num_minor_ticks: 0,
                }),
                // Hours.
                new adaptive_ticker_1.AdaptiveTicker({
                    mantissas: [1, 2, 4, 6, 8, 12],
                    base: 24.0,
                    min_interval: util_1.ONE_HOUR,
                    max_interval: 12 * util_1.ONE_HOUR,
                    num_minor_ticks: 0,
                }),
                // Days.
                new days_ticker_1.DaysTicker({ days: array_1.range(1, 32) }),
                new days_ticker_1.DaysTicker({ days: array_1.range(1, 31, 3) }),
                new days_ticker_1.DaysTicker({ days: [1, 8, 15, 22] }),
                new days_ticker_1.DaysTicker({ days: [1, 15] }),
                // Months.
                new months_ticker_1.MonthsTicker({ months: array_1.range(0, 12, 1) }),
                new months_ticker_1.MonthsTicker({ months: array_1.range(0, 12, 2) }),
                new months_ticker_1.MonthsTicker({ months: array_1.range(0, 12, 4) }),
                new months_ticker_1.MonthsTicker({ months: array_1.range(0, 12, 6) }),
                // Years
                new years_ticker_1.YearsTicker({}),
            ]; },
        });
    };
    return DatetimeTicker;
}(composite_ticker_1.CompositeTicker));
exports.DatetimeTicker = DatetimeTicker;
DatetimeTicker.initClass();
