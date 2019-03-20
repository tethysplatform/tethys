"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var linear_scale_1 = require("./linear_scale");
var CategoricalScale = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalScale, _super);
    function CategoricalScale(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalScale.initClass = function () {
        this.prototype.type = "CategoricalScale";
    };
    CategoricalScale.prototype.compute = function (x) {
        return _super.prototype.compute.call(this, this.source_range.synthetic(x));
    };
    CategoricalScale.prototype.v_compute = function (xs) {
        return _super.prototype.v_compute.call(this, this.source_range.v_synthetic(xs));
    };
    return CategoricalScale;
}(linear_scale_1.LinearScale));
exports.CategoricalScale = CategoricalScale;
CategoricalScale.initClass();
