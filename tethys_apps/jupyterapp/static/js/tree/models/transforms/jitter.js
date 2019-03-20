"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var transform_1 = require("./transform");
var factor_range_1 = require("../ranges/factor_range");
var types_1 = require("core/util/types");
var p = require("core/properties");
var bokeh_math = require("core/util/math");
var Jitter = /** @class */ (function (_super) {
    tslib_1.__extends(Jitter, _super);
    function Jitter(attrs) {
        return _super.call(this, attrs) || this;
    }
    Jitter.initClass = function () {
        this.prototype.type = "Jitter";
        this.define({
            mean: [p.Number, 0],
            width: [p.Number, 1],
            distribution: [p.Distribution, 'uniform'],
            range: [p.Instance],
        });
        this.internal({
            previous_values: [p.Array],
        });
    };
    Jitter.prototype.v_compute = function (xs0) {
        if (this.previous_values != null && this.previous_values.length == xs0.length)
            return this.previous_values;
        var xs;
        if (this.range instanceof factor_range_1.FactorRange)
            xs = this.range.v_synthetic(xs0);
        else if (types_1.isArrayableOf(xs0, types_1.isNumber))
            xs = xs0;
        else
            throw new Error("unexpected");
        var result = new Float64Array(xs.length);
        for (var i = 0; i < xs.length; i++) {
            var x = xs[i];
            result[i] = this._compute(x);
        }
        this.previous_values = result;
        return result;
    };
    Jitter.prototype.compute = function (x) {
        if (this.range instanceof factor_range_1.FactorRange)
            return this._compute(this.range.synthetic(x));
        else if (types_1.isNumber(x))
            return this._compute(x);
        else
            throw new Error("unexpected");
    };
    Jitter.prototype._compute = function (x) {
        switch (this.distribution) {
            case "uniform":
                return x + this.mean + (bokeh_math.random() - 0.5) * this.width;
            case "normal":
                return x + bokeh_math.rnorm(this.mean, this.width);
        }
    };
    return Jitter;
}(transform_1.Transform));
exports.Jitter = Jitter;
Jitter.initClass();
