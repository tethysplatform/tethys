"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var scale_1 = require("./scale");
var LinearScale = /** @class */ (function (_super) {
    tslib_1.__extends(LinearScale, _super);
    function LinearScale(attrs) {
        return _super.call(this, attrs) || this;
    }
    LinearScale.initClass = function () {
        this.prototype.type = "LinearScale";
    };
    LinearScale.prototype.compute = function (x) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1];
        return factor * x + offset;
    };
    LinearScale.prototype.v_compute = function (xs) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1];
        var result = new Float64Array(xs.length);
        for (var i = 0; i < xs.length; i++)
            result[i] = factor * xs[i] + offset;
        return result;
    };
    LinearScale.prototype.invert = function (xprime) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1];
        return (xprime - offset) / factor;
    };
    LinearScale.prototype.v_invert = function (xprimes) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1];
        var result = new Float64Array(xprimes.length);
        for (var i = 0; i < xprimes.length; i++)
            result[i] = (xprimes[i] - offset) / factor;
        return result;
    };
    LinearScale.prototype._compute_state = function () {
        //
        //  (t1 - t0)       (t1 - t0)
        //  --------- * x - --------- * s0 + t0
        //  (s1 - s0)       (s1 - s0)
        //
        // [  factor  ]     [    offset    ]
        //
        var source_start = this.source_range.start;
        var source_end = this.source_range.end;
        var target_start = this.target_range.start;
        var target_end = this.target_range.end;
        var factor = (target_end - target_start) / (source_end - source_start);
        var offset = -(factor * source_start) + target_start;
        return [factor, offset];
    };
    return LinearScale;
}(scale_1.Scale));
exports.LinearScale = LinearScale;
LinearScale.initClass();
