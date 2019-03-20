"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var linear_axis_1 = require("./linear_axis");
var datetime_tick_formatter_1 = require("../formatters/datetime_tick_formatter");
var datetime_ticker_1 = require("../tickers/datetime_ticker");
var DatetimeAxisView = /** @class */ (function (_super) {
    tslib_1.__extends(DatetimeAxisView, _super);
    function DatetimeAxisView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return DatetimeAxisView;
}(linear_axis_1.LinearAxisView));
exports.DatetimeAxisView = DatetimeAxisView;
var DatetimeAxis = /** @class */ (function (_super) {
    tslib_1.__extends(DatetimeAxis, _super);
    function DatetimeAxis(attrs) {
        return _super.call(this, attrs) || this;
    }
    DatetimeAxis.initClass = function () {
        this.prototype.type = "DatetimeAxis";
        this.prototype.default_view = DatetimeAxisView;
        this.override({
            ticker: function () { return new datetime_ticker_1.DatetimeTicker(); },
            formatter: function () { return new datetime_tick_formatter_1.DatetimeTickFormatter(); },
        });
    };
    return DatetimeAxis;
}(linear_axis_1.LinearAxis));
exports.DatetimeAxis = DatetimeAxis;
DatetimeAxis.initClass();
