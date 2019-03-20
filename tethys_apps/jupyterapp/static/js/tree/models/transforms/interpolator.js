"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var transform_1 = require("./transform");
var p = require("core/properties");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var Interpolator = /** @class */ (function (_super) {
    tslib_1.__extends(Interpolator, _super);
    function Interpolator(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this._sorted_dirty = true;
        return _this;
    }
    Interpolator.initClass = function () {
        this.prototype.type = "Interpolator";
        this.define({
            x: [p.Any],
            y: [p.Any],
            data: [p.Any],
            clip: [p.Bool, true],
        });
    };
    Interpolator.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.change, function () { return _this._sorted_dirty = true; });
    };
    Interpolator.prototype.v_compute = function (xs) {
        var result = new Float64Array(xs.length);
        for (var i = 0; i < xs.length; i++) {
            var x = xs[i];
            result[i] = this.compute(x);
        }
        return result;
    };
    Interpolator.prototype.sort = function (descending) {
        if (descending === void 0) { descending = false; }
        if (!this._sorted_dirty)
            return;
        var tsx;
        var tsy;
        if (types_1.isString(this.x) && types_1.isString(this.y) && this.data != null) {
            var column_names = this.data.columns();
            if (!array_1.includes(column_names, this.x))
                throw new Error("The x parameter does not correspond to a valid column name defined in the data parameter");
            if (!array_1.includes(column_names, this.y))
                throw new Error("The y parameter does not correspond to a valid column name defined in the data parameter");
            tsx = this.data.get_column(this.x);
            tsy = this.data.get_column(this.y);
        }
        else if (types_1.isArray(this.x) && types_1.isArray(this.y)) {
            tsx = this.x;
            tsy = this.y;
        }
        else {
            throw new Error("parameters 'x' and 'y' must be both either string fields or arrays");
        }
        if (tsx.length !== tsy.length)
            throw new Error("The length for x and y do not match");
        if (tsx.length < 2)
            throw new Error("x and y must have at least two elements to support interpolation");
        // The following sorting code is referenced from:
        // http://stackoverflow.com/questions/11499268/sort-two-arrays-the-same-way
        var list = [];
        for (var j in tsx) {
            list.push({ x: tsx[j], y: tsy[j] });
        }
        if (descending)
            list.sort(function (a, b) { return a.x > b.x ? -1 : (a.x == b.x ? 0 : 1); });
        else
            list.sort(function (a, b) { return a.x < b.x ? -1 : (a.x == b.x ? 0 : 1); });
        this._x_sorted = [];
        this._y_sorted = [];
        for (var _i = 0, list_1 = list; _i < list_1.length; _i++) {
            var _a = list_1[_i], x = _a.x, y = _a.y;
            this._x_sorted.push(x);
            this._y_sorted.push(y);
        }
        this._sorted_dirty = false;
    };
    return Interpolator;
}(transform_1.Transform));
exports.Interpolator = Interpolator;
Interpolator.initClass();
