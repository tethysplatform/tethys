"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var adaptive_ticker_1 = require("./adaptive_ticker");
var BasicTicker = /** @class */ (function (_super) {
    tslib_1.__extends(BasicTicker, _super);
    function BasicTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    BasicTicker.initClass = function () {
        this.prototype.type = "BasicTicker";
    };
    return BasicTicker;
}(adaptive_ticker_1.AdaptiveTicker));
exports.BasicTicker = BasicTicker;
BasicTicker.initClass();
