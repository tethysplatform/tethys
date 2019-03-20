"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var Callback = /** @class */ (function (_super) {
    tslib_1.__extends(Callback, _super);
    function Callback(attrs) {
        return _super.call(this, attrs) || this;
    }
    Callback.initClass = function () {
        this.prototype.type = 'Callback';
    };
    return Callback;
}(model_1.Model));
exports.Callback = Callback;
Callback.initClass();
