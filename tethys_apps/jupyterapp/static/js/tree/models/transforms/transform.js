"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var Transform = /** @class */ (function (_super) {
    tslib_1.__extends(Transform, _super);
    function Transform(attrs) {
        return _super.call(this, attrs) || this;
    }
    Transform.initClass = function () {
        this.prototype.type = "Transform";
    };
    return Transform;
}(model_1.Model));
exports.Transform = Transform;
Transform.initClass();
