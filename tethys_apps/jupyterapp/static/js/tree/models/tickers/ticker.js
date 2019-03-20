"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var Ticker = /** @class */ (function (_super) {
    tslib_1.__extends(Ticker, _super);
    function Ticker(attrs) {
        return _super.call(this, attrs) || this;
    }
    Ticker.initClass = function () {
        this.prototype.type = "Ticker";
    };
    return Ticker;
}(model_1.Model));
exports.Ticker = Ticker;
Ticker.initClass();
