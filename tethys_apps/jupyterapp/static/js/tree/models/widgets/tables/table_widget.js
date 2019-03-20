"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var widget_1 = require("../widget");
var cds_view_1 = require("../../sources/cds_view");
var p = require("core/properties");
var TableWidget = /** @class */ (function (_super) {
    tslib_1.__extends(TableWidget, _super);
    function TableWidget(attrs) {
        return _super.call(this, attrs) || this;
    }
    TableWidget.initClass = function () {
        this.prototype.type = "TableWidget";
        this.define({
            source: [p.Instance],
            view: [p.Instance, function () { return new cds_view_1.CDSView(); }],
        });
    };
    TableWidget.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        if (this.view.source == null) {
            this.view.source = this.source;
            this.view.compute_indices();
        }
    };
    return TableWidget;
}(widget_1.Widget));
exports.TableWidget = TableWidget;
TableWidget.initClass();
