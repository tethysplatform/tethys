"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var filter_1 = require("./filter");
var p = require("core/properties");
var object_1 = require("core/util/object");
var string_1 = require("core/util/string");
var CustomJSFilter = /** @class */ (function (_super) {
    tslib_1.__extends(CustomJSFilter, _super);
    function CustomJSFilter(attrs) {
        return _super.call(this, attrs) || this;
    }
    CustomJSFilter.initClass = function () {
        this.prototype.type = 'CustomJSFilter';
        this.define({
            args: [p.Any, {}],
            code: [p.String, ''],
            use_strict: [p.Boolean, false],
        });
    };
    Object.defineProperty(CustomJSFilter.prototype, "names", {
        get: function () {
            return object_1.keys(this.args);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CustomJSFilter.prototype, "values", {
        get: function () {
            return object_1.values(this.args);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CustomJSFilter.prototype, "func", {
        get: function () {
            var code = this.use_strict ? string_1.use_strict(this.code) : this.code;
            return new (Function.bind.apply(Function, [void 0].concat(this.names, ["source", "require", "exports", code])))();
        },
        enumerable: true,
        configurable: true
    });
    CustomJSFilter.prototype.compute_indices = function (source) {
        this.filter = this.func.apply(this, this.values.concat([source, require, {}]));
        return _super.prototype.compute_indices.call(this, source);
    };
    return CustomJSFilter;
}(filter_1.Filter));
exports.CustomJSFilter = CustomJSFilter;
CustomJSFilter.initClass();
