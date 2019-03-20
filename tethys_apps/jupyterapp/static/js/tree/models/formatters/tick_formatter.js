"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var TickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(TickFormatter, _super);
    function TickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    TickFormatter.initClass = function () {
        this.prototype.type = "TickFormatter";
    };
    return TickFormatter;
}(model_1.Model));
exports.TickFormatter = TickFormatter;
TickFormatter.initClass();
