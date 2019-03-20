"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var axis_1 = require("./axis");
var continuous_axis_1 = require("./continuous_axis");
var log_tick_formatter_1 = require("../formatters/log_tick_formatter");
var log_ticker_1 = require("../tickers/log_ticker");
var LogAxisView = /** @class */ (function (_super) {
    tslib_1.__extends(LogAxisView, _super);
    function LogAxisView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LogAxisView;
}(axis_1.AxisView));
exports.LogAxisView = LogAxisView;
var LogAxis = /** @class */ (function (_super) {
    tslib_1.__extends(LogAxis, _super);
    function LogAxis(attrs) {
        return _super.call(this, attrs) || this;
    }
    LogAxis.initClass = function () {
        this.prototype.type = "LogAxis";
        this.prototype.default_view = LogAxisView;
        this.override({
            ticker: function () { return new log_ticker_1.LogTicker(); },
            formatter: function () { return new log_tick_formatter_1.LogTickFormatter(); },
        });
    };
    return LogAxis;
}(continuous_axis_1.ContinuousAxis));
exports.LogAxis = LogAxis;
LogAxis.initClass();
