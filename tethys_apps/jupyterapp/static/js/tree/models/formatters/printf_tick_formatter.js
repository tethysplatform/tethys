"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var sprintf_js_1 = require("sprintf-js");
var tick_formatter_1 = require("./tick_formatter");
var p = require("core/properties");
var PrintfTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(PrintfTickFormatter, _super);
    function PrintfTickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    PrintfTickFormatter.initClass = function () {
        this.prototype.type = 'PrintfTickFormatter';
        this.define({
            format: [p.String, '%s'],
        });
    };
    PrintfTickFormatter.prototype.doFormat = function (ticks, _axis) {
        var _this = this;
        return ticks.map(function (tick) { return sprintf_js_1.sprintf(_this.format, tick); });
    };
    return PrintfTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.PrintfTickFormatter = PrintfTickFormatter;
PrintfTickFormatter.initClass();
