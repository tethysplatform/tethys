"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var transforms_1 = require("../transforms");
var p = require("core/properties");
var Scale = /** @class */ (function (_super) {
    tslib_1.__extends(Scale, _super);
    function Scale(attrs) {
        return _super.call(this, attrs) || this;
    }
    Scale.initClass = function () {
        this.prototype.type = "Scale";
        this.internal({
            source_range: [p.Any],
            target_range: [p.Any],
        });
    };
    Scale.prototype.r_compute = function (x0, x1) {
        if (this.target_range.is_reversed)
            return [this.compute(x1), this.compute(x0)];
        else
            return [this.compute(x0), this.compute(x1)];
    };
    Scale.prototype.r_invert = function (sx0, sx1) {
        if (this.target_range.is_reversed)
            return [this.invert(sx1), this.invert(sx0)];
        else
            return [this.invert(sx0), this.invert(sx1)];
    };
    return Scale;
}(transforms_1.Transform));
exports.Scale = Scale;
Scale.initClass();
