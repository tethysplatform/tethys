"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tick_formatter_1 = require("./tick_formatter");
var p = require("core/properties");
var types_1 = require("core/util/types");
var BasicTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(BasicTickFormatter, _super);
    function BasicTickFormatter(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.last_precision = 3;
        return _this;
    }
    BasicTickFormatter.initClass = function () {
        this.prototype.type = 'BasicTickFormatter';
        this.define({
            precision: [p.Any, 'auto'],
            use_scientific: [p.Bool, true],
            power_limit_high: [p.Number, 5],
            power_limit_low: [p.Number, -3],
        });
    };
    Object.defineProperty(BasicTickFormatter.prototype, "scientific_limit_low", {
        get: function () {
            return Math.pow(10.0, this.power_limit_low);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BasicTickFormatter.prototype, "scientific_limit_high", {
        get: function () {
            return Math.pow(10.0, this.power_limit_high);
        },
        enumerable: true,
        configurable: true
    });
    BasicTickFormatter.prototype.doFormat = function (ticks, _axis) {
        if (ticks.length == 0)
            return [];
        var zero_eps = 0;
        if (ticks.length >= 2)
            zero_eps = Math.abs(ticks[1] - ticks[0]) / 10000;
        var need_sci = false;
        if (this.use_scientific) {
            for (var _i = 0, ticks_1 = ticks; _i < ticks_1.length; _i++) {
                var tick = ticks_1[_i];
                var tick_abs = Math.abs(tick);
                if (tick_abs > zero_eps && (tick_abs >= this.scientific_limit_high || tick_abs <= this.scientific_limit_low)) {
                    need_sci = true;
                    break;
                }
            }
        }
        var labels = new Array(ticks.length);
        var precision = this.precision;
        if (precision == null || types_1.isNumber(precision)) {
            if (need_sci) {
                for (var i = 0, end = ticks.length; i < end; i++) {
                    labels[i] = ticks[i].toExponential(precision || undefined);
                }
            }
            else {
                for (var i = 0, end = ticks.length; i < end; i++) {
                    labels[i] = ticks[i].toFixed(precision || undefined).replace(/(\.[0-9]*?)0+$/, "$1").replace(/\.$/, "");
                }
            }
        }
        else {
            for (var x = this.last_precision, asc = this.last_precision <= 15; asc ? x <= 15 : x >= 15; asc ? x++ : x--) {
                var is_ok = true;
                if (need_sci) {
                    for (var i = 0, end = ticks.length; i < end; i++) {
                        labels[i] = ticks[i].toExponential(x);
                        if (i > 0) {
                            if (labels[i] === labels[i - 1]) {
                                is_ok = false;
                                break;
                            }
                        }
                    }
                    if (is_ok) {
                        break;
                    }
                }
                else {
                    for (var i = 0, end = ticks.length; i < end; i++) {
                        labels[i] = ticks[i].toFixed(x).replace(/(\.[0-9]*?)0+$/, "$1").replace(/\.$/, "");
                        if (i > 0) {
                            if (labels[i] == labels[i - 1]) {
                                is_ok = false;
                                break;
                            }
                        }
                    }
                    if (is_ok) {
                        break;
                    }
                }
                if (is_ok) {
                    this.last_precision = x;
                    break;
                }
            }
        }
        return labels;
    };
    return BasicTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.BasicTickFormatter = BasicTickFormatter;
BasicTickFormatter.initClass();
