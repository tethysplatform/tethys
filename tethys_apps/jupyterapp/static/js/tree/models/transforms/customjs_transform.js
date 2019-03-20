"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var transform_1 = require("./transform");
var p = require("core/properties");
var object_1 = require("core/util/object");
var string_1 = require("core/util/string");
var CustomJSTransform = /** @class */ (function (_super) {
    tslib_1.__extends(CustomJSTransform, _super);
    function CustomJSTransform(attrs) {
        return _super.call(this, attrs) || this;
    }
    CustomJSTransform.initClass = function () {
        this.prototype.type = 'CustomJSTransform';
        this.define({
            args: [p.Any, {}],
            func: [p.String, ""],
            v_func: [p.String, ""],
            use_strict: [p.Boolean, false],
        });
    };
    Object.defineProperty(CustomJSTransform.prototype, "names", {
        get: function () {
            return object_1.keys(this.args);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CustomJSTransform.prototype, "values", {
        get: function () {
            return object_1.values(this.args);
        },
        enumerable: true,
        configurable: true
    });
    CustomJSTransform.prototype._make_transform = function (name, func) {
        var code = this.use_strict ? string_1.use_strict(func) : func;
        return new (Function.bind.apply(Function, [void 0].concat(this.names, [name, "require", "exports", code])))();
    };
    Object.defineProperty(CustomJSTransform.prototype, "scalar_transform", {
        get: function () {
            return this._make_transform("x", this.func);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CustomJSTransform.prototype, "vector_transform", {
        get: function () {
            return this._make_transform("xs", this.v_func);
        },
        enumerable: true,
        configurable: true
    });
    CustomJSTransform.prototype.compute = function (x) {
        return this.scalar_transform.apply(this, this.values.concat([x, require, {}]));
    };
    CustomJSTransform.prototype.v_compute = function (xs) {
        return this.vector_transform.apply(this, this.values.concat([xs, require, {}]));
    };
    return CustomJSTransform;
}(transform_1.Transform));
exports.CustomJSTransform = CustomJSTransform;
CustomJSTransform.initClass();
