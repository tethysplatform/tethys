"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var data_source_1 = require("./data_source");
var signaling_1 = require("core/signaling");
var logging_1 = require("core/logging");
var selection_manager_1 = require("core/selection_manager");
var p = require("core/properties");
var types_1 = require("core/util/types");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var selection_1 = require("../selections/selection");
var interaction_policy_1 = require("../selections/interaction_policy");
var ColumnarDataSource = /** @class */ (function (_super) {
    tslib_1.__extends(ColumnarDataSource, _super);
    function ColumnarDataSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    ColumnarDataSource.prototype.get_array = function (key) {
        var column = this.data[key];
        if (column == null)
            this.data[key] = column = [];
        else if (!types_1.isArray(column))
            this.data[key] = column = Array.from(column);
        return column;
    };
    ColumnarDataSource.initClass = function () {
        this.prototype.type = 'ColumnarDataSource';
        this.define({
            selection_policy: [p.Instance, function () { return new interaction_policy_1.UnionRenderers(); }],
        });
        this.internal({
            selection_manager: [p.Instance, function (self) { return new selection_manager_1.SelectionManager({ source: self }); }],
            inspected: [p.Instance, function () { return new selection_1.Selection(); }],
            _shapes: [p.Any, {}],
        });
    };
    ColumnarDataSource.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._select = new signaling_1.Signal0(this, "select");
        this.inspect = new signaling_1.Signal(this, "inspect"); // XXX: <[indices, tool, renderer-view, source, data], this>
        this.streaming = new signaling_1.Signal0(this, "streaming");
        this.patching = new signaling_1.Signal(this, "patching");
    };
    ColumnarDataSource.prototype.get_column = function (colname) {
        var column = this.data[colname];
        return column != null ? column : null;
    };
    ColumnarDataSource.prototype.columns = function () {
        // return the column names in this data source
        return object_1.keys(this.data);
    };
    ColumnarDataSource.prototype.get_length = function (soft) {
        if (soft === void 0) { soft = true; }
        var lengths = array_1.uniq(object_1.values(this.data).map(function (v) { return v.length; }));
        switch (lengths.length) {
            case 0: {
                return null; // XXX: don't guess, treat on case-by-case basis
            }
            case 1: {
                return lengths[0];
            }
            default: {
                var msg = "data source has columns of inconsistent lengths";
                if (soft) {
                    logging_1.logger.warn(msg);
                    return lengths.sort()[0];
                }
                else
                    throw new Error(msg);
            }
        }
    };
    ColumnarDataSource.prototype.get_indices = function () {
        var length = this.get_length();
        return array_1.range(0, length != null ? length : 1);
        //TODO: returns [0] when no data, should it?
    };
    ColumnarDataSource.prototype.clear = function () {
        var empty = {};
        for (var _i = 0, _a = this.columns(); _i < _a.length; _i++) {
            var col = _a[_i];
            empty[col] = new this.data[col].constructor;
        }
        this.data = empty;
    };
    return ColumnarDataSource;
}(data_source_1.DataSource));
exports.ColumnarDataSource = ColumnarDataSource;
ColumnarDataSource.initClass();
