"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var Expression = /** @class */ (function (_super) {
    tslib_1.__extends(Expression, _super);
    function Expression(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this._connected = {};
        _this._result = {};
        return _this;
    }
    Expression.initClass = function () {
        this.prototype.type = "Expression";
    };
    Expression.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._connected = {};
        this._result = {};
    };
    Expression.prototype.v_compute = function (source) {
        var _this = this;
        if (this._connected[source.id] == null) {
            this.connect(source.change, function () { return delete _this._result[source.id]; });
            this.connect(source.patching, function () { return delete _this._result[source.id]; });
            this.connect(source.streaming, function () { return delete _this._result[source.id]; });
            this._connected[source.id] = true;
        }
        var result = this._result[source.id];
        if (result == null)
            this._result[source.id] = result = this._v_compute(source);
        return result;
    };
    return Expression;
}(model_1.Model));
exports.Expression = Expression;
Expression.initClass();
