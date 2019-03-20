"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var continuous_ticker_1 = require("./continuous_ticker");
var p = require("core/properties");
var SingleIntervalTicker = /** @class */ (function (_super) {
    tslib_1.__extends(SingleIntervalTicker, _super);
    function SingleIntervalTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    SingleIntervalTicker.initClass = function () {
        this.prototype.type = "SingleIntervalTicker";
        this.define({
            interval: [p.Number],
        });
    };
    SingleIntervalTicker.prototype.get_interval = function (_data_low, _data_high, _n_desired_ticks) {
        return this.interval;
    };
    Object.defineProperty(SingleIntervalTicker.prototype, "min_interval", {
        get: function () {
            return this.interval;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(SingleIntervalTicker.prototype, "max_interval", {
        get: function () {
            return this.interval;
        },
        enumerable: true,
        configurable: true
    });
    return SingleIntervalTicker;
}(continuous_ticker_1.ContinuousTicker));
exports.SingleIntervalTicker = SingleIntervalTicker;
SingleIntervalTicker.initClass();
