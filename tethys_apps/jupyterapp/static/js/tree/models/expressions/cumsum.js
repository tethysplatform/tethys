"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var expression_1 = require("./expression");
var p = require("core/properties");
var CumSum = /** @class */ (function (_super) {
    tslib_1.__extends(CumSum, _super);
    function CumSum(attrs) {
        return _super.call(this, attrs) || this;
    }
    CumSum.initClass = function () {
        this.prototype.type = "CumSum";
        this.define({
            field: [p.String],
            include_zero: [p.Boolean, false],
        });
    };
    CumSum.prototype._v_compute = function (source) {
        var result = new Float64Array(source.get_length() || 0);
        var col = source.data[this.field];
        var offset = this.include_zero ? 1 : 0;
        result[0] = this.include_zero ? 0 : col[0];
        for (var i = 1; i < result.length; i++) {
            result[i] = result[i - 1] + col[i - offset];
        }
        return result;
    };
    return CumSum;
}(expression_1.Expression));
exports.CumSum = CumSum;
CumSum.initClass();
