"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tick_formatter_1 = require("./tick_formatter");
var basic_tick_formatter_1 = require("./basic_tick_formatter");
var logging_1 = require("core/logging");
var p = require("core/properties");
var LogTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(LogTickFormatter, _super);
    function LogTickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    LogTickFormatter.initClass = function () {
        this.prototype.type = 'LogTickFormatter';
        this.define({
            ticker: [p.Instance, null],
        });
    };
    LogTickFormatter.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.basic_formatter = new basic_tick_formatter_1.BasicTickFormatter();
        if (this.ticker == null)
            logging_1.logger.warn("LogTickFormatter not configured with a ticker, using default base of 10 (labels will be incorrect if ticker base is not 10)");
    };
    LogTickFormatter.prototype.doFormat = function (ticks, axis) {
        if (ticks.length == 0)
            return [];
        var base = this.ticker != null ? this.ticker.base : 10;
        var small_interval = false;
        var labels = new Array(ticks.length);
        for (var i = 0, end = ticks.length; i < end; i++) {
            labels[i] = base + "^" + Math.round(Math.log(ticks[i]) / Math.log(base));
            if (i > 0 && labels[i] == labels[i - 1]) {
                small_interval = true;
                break;
            }
        }
        if (small_interval)
            return this.basic_formatter.doFormat(ticks, axis);
        else
            return labels;
    };
    return LogTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.LogTickFormatter = LogTickFormatter;
LogTickFormatter.initClass();
