"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var columnar_data_source_1 = require("./columnar_data_source");
var has_props_1 = require("core/has_props");
var p = require("core/properties");
var data_structures_1 = require("core/util/data_structures");
var serialization_1 = require("core/util/serialization");
var types_1 = require("core/util/types");
var typed_array = require("core/util/typed_array");
var object_1 = require("core/util/object");
//exported for testing
function stream_to_column(col, new_col, rollover) {
    if (types_1.isArray(col)) {
        var result = col.concat(new_col);
        if (rollover != null && result.length > rollover)
            return result.slice(-rollover);
        else
            return result;
    }
    else if (types_1.isTypedArray(col)) {
        var total_len = col.length + new_col.length;
        // handle rollover case for typed arrays
        if (rollover != null && total_len > rollover) {
            var start = total_len - rollover;
            var end = col.length;
            // resize col if it is shorter than the rollover length
            var result = void 0;
            if (col.length < rollover) {
                result = new (col.constructor)(rollover);
                result.set(col, 0);
            }
            else
                result = col;
            // shift values in original col to accommodate new_col
            for (var i = start, endi = end; i < endi; i++) {
                result[i - start] = result[i];
            }
            // update end values in col with new_col
            for (var i = 0, endi = new_col.length; i < endi; i++) {
                result[i + (end - start)] = new_col[i];
            }
            return result;
        }
        else {
            var tmp = new (col.constructor)(new_col);
            return typed_array.concat(col, tmp);
        }
    }
    else
        throw new Error("unsupported array types");
}
exports.stream_to_column = stream_to_column;
// exported for testing
function slice(ind, length) {
    var start, step, stop;
    if (types_1.isNumber(ind)) {
        start = ind;
        stop = ind + 1;
        step = 1;
    }
    else {
        start = ind.start != null ? ind.start : 0;
        stop = ind.stop != null ? ind.stop : length;
        step = ind.step != null ? ind.step : 1;
    }
    return [start, stop, step];
}
exports.slice = slice;
// exported for testing
function patch_to_column(col, patch, shapes) {
    var patched = new data_structures_1.Set();
    var patched_range = false;
    for (var _i = 0, patch_1 = patch; _i < patch_1.length; _i++) {
        var _a = patch_1[_i], ind = _a[0], value = _a[1];
        // make the single index case look like the length-3 multi-index case
        var item = void 0, shape = void 0;
        if (types_1.isArray(ind)) {
            var i = ind[0];
            patched.add(i);
            shape = shapes[i];
            item = col[i];
        }
        else {
            if (types_1.isNumber(ind)) {
                value = [value];
                patched.add(ind);
            }
            else
                patched_range = true;
            ind = [0, 0, ind];
            shape = [1, col.length];
            item = col;
        }
        // this is basically like NumPy's "newaxis", inserting an empty dimension
        // makes length 2 and 3 multi-index cases uniform, so that the same code
        // can handle both
        if (ind.length === 2) {
            shape = [1, shape[0]];
            ind = [ind[0], 0, ind[1]];
        }
        // now this one nested loop handles all cases
        var flat_index = 0;
        var _b = slice(ind[1], shape[0]), istart = _b[0], istop = _b[1], istep = _b[2];
        var _c = slice(ind[2], shape[1]), jstart = _c[0], jstop = _c[1], jstep = _c[2];
        for (var i = istart; i < istop; i += istep) {
            for (var j = jstart; j < jstop; j += jstep) {
                if (patched_range) {
                    patched.add(j);
                }
                item[(i * shape[1]) + j] = value[flat_index];
                flat_index++;
            }
        }
    }
    return patched;
}
exports.patch_to_column = patch_to_column;
var ColumnDataSource = /** @class */ (function (_super) {
    tslib_1.__extends(ColumnDataSource, _super);
    function ColumnDataSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    ColumnDataSource.initClass = function () {
        this.prototype.type = 'ColumnDataSource';
        this.define({
            data: [p.Any, {}],
        });
    };
    ColumnDataSource.prototype.initialize = function () {
        var _a;
        _super.prototype.initialize.call(this);
        _a = serialization_1.decode_column_data(this.data), this.data = _a[0], this._shapes = _a[1];
    };
    ColumnDataSource.prototype.attributes_as_json = function (include_defaults, value_to_json) {
        if (include_defaults === void 0) { include_defaults = true; }
        if (value_to_json === void 0) { value_to_json = ColumnDataSource._value_to_json; }
        var attrs = {};
        var obj = this.serializable_attributes();
        for (var _i = 0, _a = object_1.keys(obj); _i < _a.length; _i++) {
            var key = _a[_i];
            var value = obj[key];
            if (key === 'data')
                value = serialization_1.encode_column_data(value, this._shapes);
            if (include_defaults)
                attrs[key] = value;
            else if (key in this._set_after_defaults)
                attrs[key] = value;
        }
        return value_to_json("attributes", attrs, this);
    };
    ColumnDataSource._value_to_json = function (key, value, optional_parent_object) {
        if (types_1.isPlainObject(value) && key === 'data')
            return serialization_1.encode_column_data(value, optional_parent_object._shapes); // XXX: unknown vs. any
        else
            return has_props_1.HasProps._value_to_json(key, value, optional_parent_object);
    };
    ColumnDataSource.prototype.stream = function (new_data, rollover) {
        var data = this.data;
        for (var k in new_data) {
            data[k] = stream_to_column(data[k], new_data[k], rollover);
        }
        this.setv({ data: data }, { silent: true });
        this.streaming.emit();
    };
    ColumnDataSource.prototype.patch = function (patches) {
        var data = this.data;
        var patched = new data_structures_1.Set();
        for (var k in patches) {
            var patch = patches[k];
            patched = patched.union(patch_to_column(data[k], patch, this._shapes[k]));
        }
        this.setv({ data: data }, { silent: true });
        this.patching.emit(patched.values);
    };
    return ColumnDataSource;
}(columnar_data_source_1.ColumnarDataSource));
exports.ColumnDataSource = ColumnDataSource;
ColumnDataSource.initClass();
