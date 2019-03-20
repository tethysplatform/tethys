"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var range_1 = require("./range");
var p = require("core/properties");
var arrayable_1 = require("core/util/arrayable");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
function map_one_level(factors, padding, offset) {
    if (offset === void 0) { offset = 0; }
    var mapping = {};
    for (var i = 0; i < factors.length; i++) {
        var factor = factors[i];
        if (factor in mapping)
            throw new Error("duplicate factor or subfactor: " + factor);
        else
            mapping[factor] = { value: 0.5 + i * (1 + padding) + offset };
    }
    return [mapping, (factors.length - 1) * padding];
}
exports.map_one_level = map_one_level;
function map_two_levels(factors, outer_pad, factor_pad, offset) {
    if (offset === void 0) { offset = 0; }
    var mapping = {};
    var tops = {};
    var tops_order = [];
    for (var _i = 0, factors_1 = factors; _i < factors_1.length; _i++) {
        var _a = factors_1[_i], f0 = _a[0], f1 = _a[1];
        if (!(f0 in tops)) {
            tops[f0] = [];
            tops_order.push(f0);
        }
        tops[f0].push(f1);
    }
    var suboffset = offset;
    var total_subpad = 0;
    var _loop_1 = function (f0) {
        var n = tops[f0].length;
        var _a = map_one_level(tops[f0], factor_pad, suboffset), submap = _a[0], subpad = _a[1];
        total_subpad += subpad;
        var subtot = array_1.sum(tops[f0].map(function (f1) { return submap[f1].value; }));
        mapping[f0] = { value: subtot / n, mapping: submap };
        suboffset += n + outer_pad + subpad;
    };
    for (var _b = 0, tops_order_1 = tops_order; _b < tops_order_1.length; _b++) {
        var f0 = tops_order_1[_b];
        _loop_1(f0);
    }
    return [mapping, tops_order, (tops_order.length - 1) * outer_pad + total_subpad];
}
exports.map_two_levels = map_two_levels;
function map_three_levels(factors, outer_pad, inner_pad, factor_pad, offset) {
    if (offset === void 0) { offset = 0; }
    var mapping = {};
    var tops = {};
    var tops_order = [];
    for (var _i = 0, factors_2 = factors; _i < factors_2.length; _i++) {
        var _a = factors_2[_i], f0 = _a[0], f1 = _a[1], f2 = _a[2];
        if (!(f0 in tops)) {
            tops[f0] = [];
            tops_order.push(f0);
        }
        tops[f0].push([f1, f2]);
    }
    var mids_order = [];
    var suboffset = offset;
    var total_subpad = 0;
    var _loop_2 = function (f0) {
        var n = tops[f0].length;
        var _a = map_two_levels(tops[f0], inner_pad, factor_pad, suboffset), submap = _a[0], submids_order = _a[1], subpad = _a[2];
        for (var _i = 0, submids_order_1 = submids_order; _i < submids_order_1.length; _i++) {
            var f1 = submids_order_1[_i];
            mids_order.push([f0, f1]);
        }
        total_subpad += subpad;
        var subtot = array_1.sum(tops[f0].map(function (_a) {
            var f1 = _a[0];
            return submap[f1].value;
        }));
        mapping[f0] = { value: subtot / n, mapping: submap };
        suboffset += n + outer_pad + subpad;
    };
    for (var _b = 0, tops_order_2 = tops_order; _b < tops_order_2.length; _b++) {
        var f0 = tops_order_2[_b];
        _loop_2(f0);
    }
    return [mapping, tops_order, mids_order, (tops_order.length - 1) * outer_pad + total_subpad];
}
exports.map_three_levels = map_three_levels;
var FactorRange = /** @class */ (function (_super) {
    tslib_1.__extends(FactorRange, _super);
    function FactorRange(attrs) {
        return _super.call(this, attrs) || this;
    }
    FactorRange.initClass = function () {
        this.prototype.type = "FactorRange";
        this.define({
            factors: [p.Array, []],
            factor_padding: [p.Number, 0],
            subgroup_padding: [p.Number, 0.8],
            group_padding: [p.Number, 1.4],
            range_padding: [p.Number, 0],
            range_padding_units: [p.PaddingUnits, "percent"],
            start: [p.Number],
            end: [p.Number],
        });
        this.internal({
            levels: [p.Number],
            mids: [p.Array],
            tops: [p.Array],
            tops_groups: [p.Array],
        });
    };
    Object.defineProperty(FactorRange.prototype, "min", {
        get: function () {
            return this.start;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(FactorRange.prototype, "max", {
        get: function () {
            return this.end;
        },
        enumerable: true,
        configurable: true
    });
    FactorRange.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._init(true);
    };
    FactorRange.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.properties.factors.change, function () { return _this.reset(); });
        this.connect(this.properties.factor_padding.change, function () { return _this.reset(); });
        this.connect(this.properties.group_padding.change, function () { return _this.reset(); });
        this.connect(this.properties.subgroup_padding.change, function () { return _this.reset(); });
        this.connect(this.properties.range_padding.change, function () { return _this.reset(); });
        this.connect(this.properties.range_padding_units.change, function () { return _this.reset(); });
    };
    FactorRange.prototype.reset = function () {
        this._init(false);
        this.change.emit();
    };
    FactorRange.prototype._lookup = function (x) {
        if (x.length == 1) {
            var m = this._mapping;
            if (!m.hasOwnProperty(x[0])) {
                return NaN;
            }
            return m[x[0]].value;
        }
        else if (x.length == 2) {
            var m = this._mapping;
            if (!m.hasOwnProperty(x[0]) || !m[x[0]].mapping.hasOwnProperty(x[1])) {
                return NaN;
            }
            return m[x[0]].mapping[x[1]].value;
        }
        else if (x.length == 3) {
            var m = this._mapping;
            if (!m.hasOwnProperty(x[0]) || !m[x[0]].mapping.hasOwnProperty(x[1]) || !m[x[0]].mapping[x[1]].mapping.hasOwnProperty(x[2])) {
                return NaN;
            }
            return m[x[0]].mapping[x[1]].mapping[x[2]].value;
        }
        else
            throw new Error("unreachable code");
    };
    // convert a string factor into a synthetic coordinate
    FactorRange.prototype.synthetic = function (x) {
        if (types_1.isNumber(x))
            return x;
        if (types_1.isString(x))
            return this._lookup([x]);
        var offset = 0;
        var off = x[x.length - 1];
        if (types_1.isNumber(off)) {
            offset = off;
            x = x.slice(0, -1);
        }
        return this._lookup(x) + offset;
    };
    // convert an array of string factors into synthetic coordinates
    FactorRange.prototype.v_synthetic = function (xs) {
        var _this = this;
        return arrayable_1.map(xs, function (x) { return _this.synthetic(x); });
    };
    FactorRange.prototype._init = function (silent) {
        var _a, _b, _c;
        var levels;
        var inside_padding;
        if (array_1.all(this.factors, types_1.isString)) {
            levels = 1;
            _a = map_one_level(this.factors, this.factor_padding), this._mapping = _a[0], inside_padding = _a[1];
        }
        else if (array_1.all(this.factors, function (x) { return types_1.isArray(x) && x.length == 2 && types_1.isString(x[0]) && types_1.isString(x[1]); })) {
            levels = 2;
            _b = map_two_levels(this.factors, this.group_padding, this.factor_padding), this._mapping = _b[0], this.tops = _b[1], inside_padding = _b[2];
        }
        else if (array_1.all(this.factors, function (x) { return types_1.isArray(x) && x.length == 3 && types_1.isString(x[0]) && types_1.isString(x[1]) && types_1.isString(x[2]); })) {
            levels = 3;
            _c = map_three_levels(this.factors, this.group_padding, this.subgroup_padding, this.factor_padding), this._mapping = _c[0], this.tops = _c[1], this.mids = _c[2], inside_padding = _c[3];
        }
        else
            throw new Error("???");
        var start = 0;
        var end = this.factors.length + inside_padding;
        if (this.range_padding_units == "percent") {
            var half_span = (end - start) * this.range_padding / 2;
            start -= half_span;
            end += half_span;
        }
        else {
            start -= this.range_padding;
            end += this.range_padding;
        }
        this.setv({ start: start, end: end, levels: levels }, { silent: silent });
        if (this.bounds == "auto")
            this.setv({ bounds: [start, end] }, { silent: true });
    };
    return FactorRange;
}(range_1.Range));
exports.FactorRange = FactorRange;
FactorRange.initClass();
