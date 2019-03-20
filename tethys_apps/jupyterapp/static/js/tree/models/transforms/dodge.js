"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var transform_1 = require("./transform");
var factor_range_1 = require("../ranges/factor_range");
var p = require("core/properties");
var types_1 = require("core/util/types");
var Dodge = /** @class */ (function (_super) {
    tslib_1.__extends(Dodge, _super);
    function Dodge(attrs) {
        return _super.call(this, attrs) || this;
    }
    Dodge.initClass = function () {
        this.prototype.type = "Dodge";
        this.define({
            value: [p.Number, 0],
            range: [p.Instance],
        });
    };
    // XXX: this is repeated in ./jitter.ts
    Dodge.prototype.v_compute = function (xs0) {
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
        return result;
    };
    Dodge.prototype.compute = function (x) {
        if (this.range instanceof factor_range_1.FactorRange)
            return this._compute(this.range.synthetic(x));
        else if (types_1.isNumber(x))
            return this._compute(x);
        else
            throw new Error("unexpected");
    };
    Dodge.prototype._compute = function (x) {
        return x + this.value;
    };
    return Dodge;
}(transform_1.Transform));
exports.Dodge = Dodge;
Dodge.initClass();
