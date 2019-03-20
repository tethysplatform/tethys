"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tick_formatter_1 = require("./tick_formatter");
var array_1 = require("core/util/array");
var CategoricalTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalTickFormatter, _super);
    function CategoricalTickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalTickFormatter.initClass = function () {
        this.prototype.type = 'CategoricalTickFormatter';
    };
    CategoricalTickFormatter.prototype.doFormat = function (ticks, _axis) {
        return array_1.copy(ticks);
    };
    return CategoricalTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.CategoricalTickFormatter = CategoricalTickFormatter;
CategoricalTickFormatter.initClass();
