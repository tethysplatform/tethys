"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var Numbro = require("numbro");
var tick_formatter_1 = require("./tick_formatter");
var p = require("core/properties");
var NumeralTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(NumeralTickFormatter, _super);
    function NumeralTickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    NumeralTickFormatter.initClass = function () {
        this.prototype.type = 'NumeralTickFormatter';
        this.define({
            // TODO (bev) all of these could be tightened up
            format: [p.String, '0,0'],
            language: [p.String, 'en'],
            rounding: [p.String, 'round'],
        });
    };
    Object.defineProperty(NumeralTickFormatter.prototype, "_rounding_fn", {
        get: function () {
            switch (this.rounding) {
                case "round":
                case "nearest":
                    return Math.round;
                case "floor":
                case "rounddown":
                    return Math.floor;
                case "ceil":
                case "roundup":
                    return Math.ceil;
            }
        },
        enumerable: true,
        configurable: true
    });
    NumeralTickFormatter.prototype.doFormat = function (ticks, _axis) {
        var _a = this, format = _a.format, language = _a.language, _rounding_fn = _a._rounding_fn;
        return ticks.map(function (tick) { return Numbro.format(tick, format, language, _rounding_fn); });
    };
    return NumeralTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.NumeralTickFormatter = NumeralTickFormatter;
NumeralTickFormatter.initClass();
