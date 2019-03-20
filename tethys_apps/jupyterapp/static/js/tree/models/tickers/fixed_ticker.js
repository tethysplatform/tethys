"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var continuous_ticker_1 = require("./continuous_ticker");
var p = require("core/properties");
var FixedTicker = /** @class */ (function (_super) {
    tslib_1.__extends(FixedTicker, _super);
    function FixedTicker(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.min_interval = 0;
        _this.max_interval = 0;
        return _this;
    }
    FixedTicker.initClass = function () {
        this.prototype.type = "FixedTicker";
        this.define({
            ticks: [p.Array, []],
            minor_ticks: [p.Array, []],
        });
    };
    FixedTicker.prototype.get_ticks_no_defaults = function (_data_low, _data_high, _cross_loc, _desired_n_ticks) {
        return {
            major: this.ticks,
            minor: this.minor_ticks,
        };
    };
    // XXX: whatever, because FixedTicker needs to fullfill the interface somehow
    FixedTicker.prototype.get_interval = function (_data_low, _data_high, _desired_n_ticks) {
        return 0;
    };
    return FixedTicker;
}(continuous_ticker_1.ContinuousTicker));
exports.FixedTicker = FixedTicker;
FixedTicker.initClass();
