"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var columnar_data_source_1 = require("../sources/columnar_data_source");
var vectorization_1 = require("core/vectorization");
var p = require("core/properties");
var logging_1 = require("core/logging");
var array_1 = require("core/util/array");
var LegendItem = /** @class */ (function (_super) {
    tslib_1.__extends(LegendItem, _super);
    function LegendItem(attrs) {
        return _super.call(this, attrs) || this;
    }
    LegendItem.initClass = function () {
        this.prototype.type = "LegendItem";
        this.define({
            label: [p.StringSpec, null],
            renderers: [p.Array, []],
            index: [p.Number, null],
        });
    };
    LegendItem.prototype._check_data_sources_on_renderers = function () {
        var field = this.get_field_from_label_prop();
        if (field != null) {
            if (this.renderers.length < 1) {
                return false;
            }
            var source = this.renderers[0].data_source;
            if (source != null) {
                for (var _i = 0, _a = this.renderers; _i < _a.length; _i++) {
                    var r = _a[_i];
                    if (r.data_source != source) {
                        return false;
                    }
                }
            }
        }
        return true;
    };
    LegendItem.prototype._check_field_label_on_data_source = function () {
        var field = this.get_field_from_label_prop();
        if (field != null) {
            if (this.renderers.length < 1) {
                return false;
            }
            var source = this.renderers[0].data_source;
            if (source != null && !array_1.includes(source.columns(), field)) {
                return false;
            }
        }
        return true;
    };
    LegendItem.prototype.initialize = function () {
        var _this = this;
        _super.prototype.initialize.call(this);
        this.legend = null;
        this.connect(this.change, function () { if (_this.legend != null)
            _this.legend.item_change.emit(); });
        // Validate data_sources match
        var data_source_validation = this._check_data_sources_on_renderers();
        if (!data_source_validation)
            logging_1.logger.error("Non matching data sources on legend item renderers");
        // Validate label in data_source
        var field_validation = this._check_field_label_on_data_source();
        if (!field_validation)
            logging_1.logger.error("Bad column name on label: " + this.label);
    };
    LegendItem.prototype.get_field_from_label_prop = function () {
        var label = this.label;
        return vectorization_1.isField(label) ? label.field : null;
    };
    LegendItem.prototype.get_labels_list_from_label_prop = function () {
        // Always return a list of the labels
        if (vectorization_1.isValue(this.label))
            return [this.label.value];
        var field = this.get_field_from_label_prop();
        if (field != null) {
            var source = void 0;
            if (this.renderers[0] && this.renderers[0].data_source != null)
                source = this.renderers[0].data_source;
            else
                return ["No source found"];
            if (source instanceof columnar_data_source_1.ColumnarDataSource) {
                var data = source.get_column(field);
                if (data != null)
                    return array_1.uniq(Array.from(data));
                else
                    return ["Invalid field"];
            }
        }
        return [];
    };
    return LegendItem;
}(model_1.Model));
exports.LegendItem = LegendItem;
LegendItem.initClass();
