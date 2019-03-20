"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var p = require("core/properties");
var selection_1 = require("../selections/selection");
var array_1 = require("core/util/array");
var columnar_data_source_1 = require("./columnar_data_source");
var CDSView = /** @class */ (function (_super) {
    tslib_1.__extends(CDSView, _super);
    function CDSView(attrs) {
        return _super.call(this, attrs) || this;
    }
    CDSView.initClass = function () {
        this.prototype.type = 'CDSView';
        this.define({
            filters: [p.Array, []],
            source: [p.Instance],
        });
        this.internal({
            indices: [p.Array, []],
            indices_map: [p.Any, {}],
        });
    };
    CDSView.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.compute_indices();
    };
    CDSView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.properties.filters.change, function () {
            _this.compute_indices();
            _this.change.emit();
        });
        if (this.source != null) {
            if (this.source.change != null)
                this.connect(this.source.change, function () { return _this.compute_indices(); });
            if (this.source.streaming != null)
                this.connect(this.source.streaming, function () { return _this.compute_indices(); });
            if (this.source.patching != null)
                this.connect(this.source.patching, function () { return _this.compute_indices(); });
        }
    };
    CDSView.prototype.compute_indices = function () {
        var _this = this;
        var indices = (this.filters.map(function (filter) { return filter.compute_indices(_this.source); }));
        indices = ((function () {
            var result = [];
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var inds = indices_1[_i];
                if (inds != null) {
                    result.push(inds);
                }
            }
            return result;
        })());
        if (indices.length > 0) {
            this.indices = array_1.intersection.apply(this, indices);
        }
        else {
            if (this.source instanceof columnar_data_source_1.ColumnarDataSource) {
                this.indices = this.source.get_indices();
            }
        }
        this.indices_map_to_subset();
    };
    CDSView.prototype.indices_map_to_subset = function () {
        this.indices_map = {};
        for (var i = 0; i < this.indices.length; i++) {
            this.indices_map[this.indices[i]] = i;
        }
    };
    CDSView.prototype.convert_selection_from_subset = function (selection_subset) {
        var _this = this;
        var selection_full = new selection_1.Selection();
        selection_full.update_through_union(selection_subset);
        var indices_1d = (selection_subset.indices.map(function (i) { return _this.indices[i]; }));
        selection_full.indices = indices_1d;
        selection_full.image_indices = selection_subset.image_indices;
        return selection_full;
    };
    CDSView.prototype.convert_selection_to_subset = function (selection_full) {
        var _this = this;
        var selection_subset = new selection_1.Selection();
        selection_subset.update_through_union(selection_full);
        var indices_1d = (selection_full.indices.map(function (i) { return _this.indices_map[i]; }));
        selection_subset.indices = indices_1d;
        selection_subset.image_indices = selection_full.image_indices;
        return selection_subset;
    };
    CDSView.prototype.convert_indices_from_subset = function (indices) {
        var _this = this;
        return indices.map(function (i) { return _this.indices[i]; });
    };
    return CDSView;
}(model_1.Model));
exports.CDSView = CDSView;
CDSView.initClass();
