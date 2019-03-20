"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var expression_1 = require("./expression");
var p = require("core/properties");
var Stack = /** @class */ (function (_super) {
    tslib_1.__extends(Stack, _super);
    function Stack(attrs) {
        return _super.call(this, attrs) || this;
    }
    Stack.initClass = function () {
        this.prototype.type = "Stack";
        this.define({
            fields: [p.Array, []],
        });
    };
    Stack.prototype._v_compute = function (source) {
        var result = new Float64Array(source.get_length() || 0);
        for (var _i = 0, _a = this.fields; _i < _a.length; _i++) {
            var f = _a[_i];
            for (var i = 0; i < source.data[f].length; i++) {
                var x = source.data[f][i];
                result[i] += x;
            }
        }
        return result;
    };
    return Stack;
}(expression_1.Expression));
exports.Stack = Stack;
Stack.initClass();
