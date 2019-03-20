"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tick_formatter_1 = require("./tick_formatter");
var p = require("core/properties");
var object_1 = require("core/util/object");
var string_1 = require("core/util/string");
var FuncTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(FuncTickFormatter, _super);
    function FuncTickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    FuncTickFormatter.initClass = function () {
        this.prototype.type = 'FuncTickFormatter';
        this.define({
            args: [p.Any, {}],
            code: [p.String, ''],
            use_strict: [p.Boolean, false],
        });
    };
    Object.defineProperty(FuncTickFormatter.prototype, "names", {
        get: function () {
            return object_1.keys(this.args);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(FuncTickFormatter.prototype, "values", {
        get: function () {
            return object_1.values(this.args);
        },
        enumerable: true,
        configurable: true
    });
    FuncTickFormatter.prototype._make_func = function () {
        var code = this.use_strict ? string_1.use_strict(this.code) : this.code;
        return new (Function.bind.apply(Function, [void 0, "tick", "index", "ticks"].concat(this.names, ["require", "exports", code])))();
    };
    FuncTickFormatter.prototype.doFormat = function (ticks, _axis) {
        var _this = this;
        var cache = {};
        var func = this._make_func().bind(cache);
        return ticks.map(function (tick, index, ticks) { return func.apply(void 0, [tick, index, ticks].concat(_this.values, [require, {}])); });
    };
    return FuncTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.FuncTickFormatter = FuncTickFormatter;
FuncTickFormatter.initClass();
