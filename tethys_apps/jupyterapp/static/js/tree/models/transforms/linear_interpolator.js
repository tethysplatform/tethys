"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var array_1 = require("core/util/array");
var interpolator_1 = require("./interpolator");
var LinearInterpolator = /** @class */ (function (_super) {
    tslib_1.__extends(LinearInterpolator, _super);
    function LinearInterpolator(attrs) {
        return _super.call(this, attrs) || this;
    }
    LinearInterpolator.initClass = function () {
        this.prototype.type = "LinearInterpolator";
    };
    LinearInterpolator.prototype.compute = function (x) {
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
        if (x == this._x_sorted[0])
            return this._y_sorted[0];
        var ind = array_1.findLastIndex(this._x_sorted, function (num) { return num < x; });
        var x1 = this._x_sorted[ind];
        var x2 = this._x_sorted[ind + 1];
        var y1 = this._y_sorted[ind];
        var y2 = this._y_sorted[ind + 1];
        return y1 + (((x - x1) / (x2 - x1)) * (y2 - y1));
    };
    return LinearInterpolator;
}(interpolator_1.Interpolator));
exports.LinearInterpolator = LinearInterpolator;
LinearInterpolator.initClass();
