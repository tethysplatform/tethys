"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var SlickGrid = require("slickgrid").Grid;
var RowSelectionModel = require("slickgrid/plugins/slick.rowselectionmodel").RowSelectionModel;
var CheckboxSelectColumn = require("slickgrid/plugins/slick.checkboxselectcolumn").CheckboxSelectColumn;
var p = require("core/properties");
var string_1 = require("core/util/string");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var logging_1 = require("core/logging");
var table_widget_1 = require("./table_widget");
var widget_1 = require("../widget");
exports.DTINDEX_NAME = "__bkdt_internal_index__";
var DataProvider = /** @class */ (function () {
    function DataProvider(source, view) {
        this.source = source;
        this.view = view;
        if (exports.DTINDEX_NAME in this.source.data)
            throw new Error("special name " + exports.DTINDEX_NAME + " cannot be used as a data table column");
        this.index = this.view.indices;
    }
    DataProvider.prototype.getLength = function () {
        return this.index.length;
    };
    DataProvider.prototype.getItem = function (offset) {
        var item = {};
        for (var _i = 0, _a = object_1.keys(this.source.data); _i < _a.length; _i++) {
            var field = _a[_i];
            item[field] = this.source.data[field][this.index[offset]];
        }
        item[exports.DTINDEX_NAME] = this.index[offset];
        return item;
    };
    DataProvider.prototype.setItem = function (offset, item) {
        for (var field in item) {
            // internal index is maintained independently, ignore
            var value = item[field];
            if (field != exports.DTINDEX_NAME) {
                this.source.data[field][this.index[offset]] = value;
            }
        }
        this._update_source_inplace();
    };
    DataProvider.prototype.getField = function (offset, field) {
        if (field == exports.DTINDEX_NAME) {
            return this.index[offset];
        }
        return this.source.data[field][this.index[offset]];
    };
    DataProvider.prototype.setField = function (offset, field, value) {
        // field assumed never to be internal index name (ctor would throw)
        this.source.data[field][this.index[offset]] = value;
        this._update_source_inplace();
    };
    DataProvider.prototype.getItemMetadata = function (_index) {
        return null;
    };
    DataProvider.prototype.getRecords = function () {
        var _this = this;
        return array_1.range(0, this.getLength()).map(function (i) { return _this.getItem(i); });
    };
    DataProvider.prototype.sort = function (columns) {
        var cols = columns.map(function (column) { return [column.sortCol.field, column.sortAsc ? 1 : -1]; });
        if (cols.length == 0) {
            cols = [[exports.DTINDEX_NAME, 1]];
        }
        var records = this.getRecords();
        var old_index = this.index.slice();
        this.index.sort(function (i1, i2) {
            for (var _i = 0, cols_1 = cols; _i < cols_1.length; _i++) {
                var _a = cols_1[_i], field = _a[0], sign = _a[1];
                var value1 = records[old_index.indexOf(i1)][field];
                var value2 = records[old_index.indexOf(i2)][field];
                var result = value1 == value2 ? 0 : value1 > value2 ? sign : -sign;
                if (result != 0)
                    return result;
            }
            return 0;
        });
    };
    DataProvider.prototype._update_source_inplace = function () {
        this.source.properties.data.change.emit();
    };
    return DataProvider;
}());
exports.DataProvider = DataProvider;
var DataTableView = /** @class */ (function (_super) {
    tslib_1.__extends(DataTableView, _super);
    function DataTableView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._in_selection_update = false;
        _this._warned_not_reorderable = false;
        return _this;
    }
    DataTableView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
        this.connect(this.model.source.streaming, function () { return _this.updateGrid(); });
        this.connect(this.model.source.patching, function () { return _this.updateGrid(); });
        this.connect(this.model.source.change, function () { return _this.updateGrid(true); });
        this.connect(this.model.source.properties.data.change, function () { return _this.updateGrid(); });
        this.connect(this.model.source.selected.change, function () { return _this.updateSelection(); });
    };
    DataTableView.prototype.updateGrid = function (from_source_change) {
        if (from_source_change === void 0) { from_source_change = false; }
        // TODO (bev) This is to enure that CDSView indices are properly computed
        // before passing to the DataProvider. This will result in extra calls to
        // compute_indices. This "over execution" will be addressed in a more
        // general look at events
        this.model.view.compute_indices();
        this.data.constructor(this.model.source, this.model.view);
        this.grid.invalidate();
        this.grid.render();
        if (!from_source_change) {
            // This is only needed to call @_tell_document_about_change()
            this.model.source.data = this.model.source.data;
            this.model.source.change.emit();
        }
    };
    DataTableView.prototype.updateSelection = function () {
        var _this = this;
        if (this._in_selection_update)
            return;
        var selected = this.model.source.selected;
        var permuted_indices = selected.indices.map(function (x) { return _this.data.index.indexOf(x); });
        this._in_selection_update = true;
        this.grid.setSelectedRows(permuted_indices);
        this._in_selection_update = false;
        // If the selection is not in the current slickgrid viewport, scroll the
        // datatable to start at the row before the first selected row, so that
        // the selection is immediately brought into view. We don't scroll when
        // the selection is already in the viewport so that selecting from the
        // datatable itself does not re-scroll.
        var cur_grid_range = this.grid.getViewport();
        var scroll_index = this.model.get_scroll_index(cur_grid_range, permuted_indices);
        if (scroll_index != null)
            this.grid.scrollRowToTop(scroll_index);
    };
    DataTableView.prototype.newIndexColumn = function () {
        return {
            id: string_1.uniqueId(),
            name: this.model.index_header,
            field: exports.DTINDEX_NAME,
            width: this.model.index_width,
            behavior: "select",
            cannotTriggerInsert: true,
            resizable: false,
            selectable: false,
            sortable: true,
            cssClass: "bk-cell-index",
            headerCssClass: "bk-header-index",
        };
    };
    DataTableView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-data-table");
    };
    DataTableView.prototype.render = function () {
        var _this = this;
        var checkboxSelector;
        var columns = this.model.columns.map(function (column) { return column.toColumn(); });
        if (this.model.selectable == "checkbox") {
            checkboxSelector = new CheckboxSelectColumn({ cssClass: "bk-cell-select" });
            columns.unshift(checkboxSelector.getColumnDefinition());
        }
        if (this.model.index_position != null) {
            var index_position = this.model.index_position;
            var index = this.newIndexColumn();
            // This is to be able to provide negative index behaviour that
            // matches what python users will expect
            if (index_position == -1) {
                columns.push(index);
            }
            else if (index_position < -1) {
                columns.splice(index_position + 1, 0, index);
            }
            else {
                columns.splice(index_position, 0, index);
            }
        }
        var reorderable = this.model.reorderable;
        if (reorderable && !(typeof $ !== "undefined" && $.fn != null && $.fn.sortable != null)) {
            if (!this._warned_not_reorderable) {
                logging_1.logger.warn("jquery-ui is required to enable DataTable.reorderable");
                this._warned_not_reorderable = true;
            }
            reorderable = false;
        }
        var options = {
            enableCellNavigation: this.model.selectable !== false,
            enableColumnReorder: reorderable,
            forceFitColumns: this.model.fit_columns,
            autoHeight: this.model.height == "auto",
            multiColumnSort: this.model.sortable,
            editable: this.model.editable,
            autoEdit: false,
        };
        if (this.model.width != null)
            this.el.style.width = this.model.width + "px";
        else
            this.el.style.width = this.model.default_width + "px";
        if (this.model.height != null && this.model.height != "auto")
            this.el.style.height = this.model.height + "px";
        this.data = new DataProvider(this.model.source, this.model.view);
        this.grid = new SlickGrid(this.el, this.data, columns, options);
        this.grid.onSort.subscribe(function (_event, args) {
            columns = args.sortCols;
            _this.data.sort(columns);
            _this.grid.invalidate();
            _this.updateSelection();
            _this.grid.render();
            if (!_this.model.header_row) {
                _this._hide_header();
            }
        });
        if (this.model.selectable !== false) {
            this.grid.setSelectionModel(new RowSelectionModel({ selectActiveRow: checkboxSelector == null }));
            if (checkboxSelector != null)
                this.grid.registerPlugin(checkboxSelector);
            this.grid.onSelectedRowsChanged.subscribe(function (_event, args) {
                if (_this._in_selection_update) {
                    return;
                }
                _this.model.source.selected.indices = args.rows.map(function (i) { return _this.data.index[i]; });
            });
            this.updateSelection();
            if (!this.model.header_row) {
                this._hide_header();
            }
        }
    };
    DataTableView.prototype._hide_header = function () {
        for (var _i = 0, _a = Array.from(this.el.querySelectorAll('.slick-header-columns')); _i < _a.length; _i++) {
            var el = _a[_i];
            el.style.height = "0px";
        }
        this.grid.resizeCanvas();
    };
    return DataTableView;
}(widget_1.WidgetView));
exports.DataTableView = DataTableView;
var DataTable = /** @class */ (function (_super) {
    tslib_1.__extends(DataTable, _super);
    function DataTable(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.default_width = 600;
        return _this;
    }
    DataTable.initClass = function () {
        this.prototype.type = 'DataTable';
        this.prototype.default_view = DataTableView;
        this.define({
            columns: [p.Array, []],
            fit_columns: [p.Bool, true],
            sortable: [p.Bool, true],
            reorderable: [p.Bool, true],
            editable: [p.Bool, false],
            selectable: [p.Any, true],
            index_position: [p.Int, 0],
            index_header: [p.String, "#"],
            index_width: [p.Int, 40],
            scroll_to_selection: [p.Bool, true],
            header_row: [p.Bool, true],
        });
        this.override({
            height: 400,
        });
    };
    DataTable.prototype.get_scroll_index = function (grid_range, selected_indices) {
        if (!this.scroll_to_selection || (selected_indices.length == 0))
            return null;
        if (!array_1.any(selected_indices, function (i) { return grid_range.top <= i && i <= grid_range.bottom; })) {
            return Math.max(0, Math.min.apply(Math, selected_indices) - 1);
        }
        return null;
    };
    return DataTable;
}(table_widget_1.TableWidget));
exports.DataTable = DataTable;
DataTable.initClass();
