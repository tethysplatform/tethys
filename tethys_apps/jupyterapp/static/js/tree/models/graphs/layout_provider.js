"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var LayoutProvider = /** @class */ (function (_super) {
    tslib_1.__extends(LayoutProvider, _super);
    function LayoutProvider(attrs) {
        return _super.call(this, attrs) || this;
    }
    LayoutProvider.initClass = function () {
        this.prototype.type = "LayoutProvider";
    };
    return LayoutProvider;
}(model_1.Model));
exports.LayoutProvider = LayoutProvider;
LayoutProvider.initClass();
