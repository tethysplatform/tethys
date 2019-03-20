"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var interpolator_1 = require("./interpolator");
var p = require("core/properties");
var array_1 = require("core/util/array");
var StepInterpolator = /** @class */ (function (_super) {
    tslib_1.__extends(StepInterpolator, _super);
    function StepInterpolator(attrs) {
        return _super.call(this, attrs) || this;
    }
    StepInterpolator.initClass = function () {
        this.prototype.type = "StepInterpolator";
        this.define({
            mode: [p.StepMode, "after"],
        });
    };
    StepInterpolator.prototype.compute = function (x) {
        this.sort(false);
        if (this.clip) {
            if (x < this._x_sorted[0] || x > this._x_sorted[this._x_sorted.length - 1])
                return NaN;
        }
        else {
            if (x < this._x_sorted[0])
                return this._y_sorted[0];
            if (x > this._x_sorted[this._x_sorted.length - 1])
                return this._y_sorted[this._y_sorted.length - 1];
        }
        var ind;
        switch (this.mode) {
            case "after": {
                ind = array_1.findLastIndex(this._x_sorted, function (num) { return x >= num; });
                break;
            }
            case "before": {
                ind = array_1.findIndex(this._x_sorted, function (num) { return x <= num; });
                break;
            }
            case "center": {
                var diffs = this._x_sorted.map(function (tx) { return Math.abs(tx - x); });
                var mdiff_1 = array_1.min(diffs);
                ind = array_1.findIndex(diffs, function (num) { return mdiff_1 === num; });
                break;
            }
            default:
                throw new Error("unknown mode: " + this.mode);
        }
        return ind != -1 ? this._y_sorted[ind] : NaN;
    };
    return StepInterpolator;
}(interpolator_1.Interpolator));
exports.StepInterpolator = StepInterpolator;
StepInterpolator.initClass();
