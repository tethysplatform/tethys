"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var ticker_1 = require("./ticker");
var CategoricalTicker = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalTicker, _super);
    function CategoricalTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalTicker.initClass = function () {
        this.prototype.type = "CategoricalTicker";
    };
    CategoricalTicker.prototype.get_ticks = function (start, end, range, _cross_loc, _) {
        var majors = this._collect(range.factors, range, start, end);
        var tops = this._collect(range.tops || [], range, start, end);
        var mids = this._collect(range.mids || [], range, start, end);
        return {
            major: majors,
            minor: [],
            tops: tops,
            mids: mids,
        };
    };
    CategoricalTicker.prototype._collect = function (factors, range, start, end) {
        var result = [];
        for (var _i = 0, factors_1 = factors; _i < factors_1.length; _i++) {
            var factor = factors_1[_i];
            var coord = range.synthetic(factor);
            if (coord > start && coord < end)
                result.push(factor);
        }
        return result;
    };
    return CategoricalTicker;
}(ticker_1.Ticker));
exports.CategoricalTicker = CategoricalTicker;
CategoricalTicker.initClass();
