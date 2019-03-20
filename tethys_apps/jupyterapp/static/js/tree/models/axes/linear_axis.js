"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var axis_1 = require("./axis");
var continuous_axis_1 = require("./continuous_axis");
var basic_tick_formatter_1 = require("../formatters/basic_tick_formatter");
var basic_ticker_1 = require("../tickers/basic_ticker");
var LinearAxisView = /** @class */ (function (_super) {
    tslib_1.__extends(LinearAxisView, _super);
    function LinearAxisView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LinearAxisView;
}(axis_1.AxisView));
exports.LinearAxisView = LinearAxisView;
var LinearAxis = /** @class */ (function (_super) {
    tslib_1.__extends(LinearAxis, _super);
    function LinearAxis(attrs) {
        return _super.call(this, attrs) || this;
    }
    LinearAxis.initClass = function () {
        this.prototype.type = "LinearAxis";
        this.prototype.default_view = LinearAxisView;
        this.override({
            ticker: function () { return new basic_ticker_1.BasicTicker(); },
            formatter: function () { return new basic_tick_formatter_1.BasicTickFormatter(); },
        });
    };
    return LinearAxis;
}(continuous_axis_1.ContinuousAxis));
exports.LinearAxis = LinearAxis;
LinearAxis.initClass();
