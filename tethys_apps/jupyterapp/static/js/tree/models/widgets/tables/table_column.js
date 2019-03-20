"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var cell_formatters_1 = require("./cell_formatters");
var cell_editors_1 = require("./cell_editors");
var p = require("core/properties");
var string_1 = require("core/util/string");
var model_1 = require("../../../model");
var TableColumn = /** @class */ (function (_super) {
    tslib_1.__extends(TableColumn, _super);
    function TableColumn(attrs) {
        return _super.call(this, attrs) || this;
    }
    TableColumn.initClass = function () {
        this.prototype.type = 'TableColumn';
        this.define({
            field: [p.String],
            title: [p.String],
            width: [p.Number, 300],
            formatter: [p.Instance, function () { return new cell_formatters_1.StringFormatter(); }],
            editor: [p.Instance, function () { return new cell_editors_1.StringEditor(); }],
            sortable: [p.Bool, true],
            default_sort: [p.String, "ascending"],
        });
    };
    TableColumn.prototype.toColumn = function () {
        return {
            id: string_1.uniqueId(),
            field: this.field,
            name: this.title,
            width: this.width,
            formatter: this.formatter != null ? this.formatter.doFormat.bind(this.formatter) : undefined,
            model: this.editor,
            editor: this.editor.default_view,
            sortable: this.sortable,
            defaultSortAsc: this.default_sort == "ascending",
        };
    };
    return TableColumn;
}(model_1.Model));
exports.TableColumn = TableColumn;
TableColumn.initClass();
