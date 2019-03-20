"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var callback_1 = require("./callback");
var p = require("core/properties");
var object_1 = require("core/util/object");
var string_1 = require("core/util/string");
var CustomJS = /** @class */ (function (_super) {
    tslib_1.__extends(CustomJS, _super);
    function CustomJS(attrs) {
        return _super.call(this, attrs) || this;
    }
    CustomJS.initClass = function () {
        this.prototype.type = 'CustomJS';
        this.define({
            args: [p.Any, {}],
            code: [p.String, ''],
            use_strict: [p.Boolean, false],
        });
    };
    Object.defineProperty(CustomJS.prototype, "names", {
        get: function () {
            return object_1.keys(this.args);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CustomJS.prototype, "values", {
        get: function () {
            return object_1.values(this.args);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CustomJS.prototype, "func", {
        get: function () {
            var code = this.use_strict ? string_1.use_strict(this.code) : this.code;
            return new (Function.bind.apply(Function, [void 0].concat(this.names, ["cb_obj", "cb_data", "require", "exports", code])))();
        },
        enumerable: true,
        configurable: true
    });
    CustomJS.prototype.execute = function (cb_obj, cb_data) {
        return this.func.apply(cb_obj, this.values.concat(cb_obj, cb_data, require, {}));
    };
    return CustomJS;
}(callback_1.Callback));
exports.CustomJS = CustomJS;
CustomJS.initClass();
