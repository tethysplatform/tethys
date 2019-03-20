"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../../model");
var p = require("core/properties");
var object_1 = require("core/util/object");
var string_1 = require("core/util/string");
var CustomJSHover = /** @class */ (function (_super) {
    tslib_1.__extends(CustomJSHover, _super);
    function CustomJSHover(attrs) {
        return _super.call(this, attrs) || this;
    }
    CustomJSHover.initClass = function () {
        this.prototype.type = 'CustomJSHover';
        this.define({
            args: [p.Any, {}],
            code: [p.String, ""],
        });
    };
    Object.defineProperty(CustomJSHover.prototype, "values", {
        get: function () {
            return object_1.values(this.args);
        },
        enumerable: true,
        configurable: true
    });
    CustomJSHover.prototype._make_code = function (valname, formatname, varsname, fn) {
        // this relies on keys(args) and values(args) returning keys and values
        // in the same order
        return new (Function.bind.apply(Function, [void 0].concat(object_1.keys(this.args), [valname, formatname, varsname, "require", "exports", string_1.use_strict(fn)])))();
    };
    CustomJSHover.prototype.format = function (value, format, special_vars) {
        var formatter = this._make_code("value", "format", "special_vars", this.code);
        return formatter.apply(void 0, this.values.concat([value, format, special_vars, require, exports]));
    };
    return CustomJSHover;
}(model_1.Model));
exports.CustomJSHover = CustomJSHover;
CustomJSHover.initClass();
