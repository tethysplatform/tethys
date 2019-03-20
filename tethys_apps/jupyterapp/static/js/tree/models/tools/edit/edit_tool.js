"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var gesture_tool_1 = require("../gestures/gesture_tool");
var EditToolView = /** @class */ (function (_super) {
    tslib_1.__extends(EditToolView, _super);
    function EditToolView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._mouse_in_frame = true;
        return _this;
    }
    EditToolView.prototype._move_enter = function (_e) {
        this._mouse_in_frame = true;
    };
    EditToolView.prototype._move_exit = function (_e) {
        this._mouse_in_frame = false;
    };
    EditToolView.prototype._map_drag = function (sx, sy, renderer) {
        // Maps screen to data coordinates
        var frame = this.plot_model.frame;
        if (!frame.bbox.contains(sx, sy)) {
            return null;
        }
        var x = frame.xscales[renderer.x_range_name].invert(sx);
        var y = frame.yscales[renderer.y_range_name].invert(sy);
        return [x, y];
    };
    EditToolView.prototype._delete_selected = function (renderer) {
        // Deletes all selected rows in the ColumnDataSource
        var cds = renderer.data_source;
        var indices = cds.selected.indices;
        indices.sort();
        for (var _i = 0, _a = cds.columns(); _i < _a.length; _i++) {
            var column = _a[_i];
            var values = cds.get_array(column);
            for (var index = 0; index < indices.length; index++) {
                var ind = indices[index];
                values.splice(ind - index, 1);
            }
        }
        this._emit_cds_changes(cds);
    };
    EditToolView.prototype._pop_glyphs = function (cds, num_objects) {
        // Pops rows in the CDS until only num_objects are left
        var columns = cds.columns();
        if (!num_objects || !columns.length)
            return;
        for (var _i = 0, columns_1 = columns; _i < columns_1.length; _i++) {
            var column = columns_1[_i];
            var array = cds.get_array(column);
            var drop = array.length - num_objects + 1;
            if (drop < 1)
                continue;
            if (!types_1.isArray(array)) {
                array = Array.from(array);
                cds.data[column] = array;
            }
            array.splice(0, drop);
        }
    };
    EditToolView.prototype._emit_cds_changes = function (cds, redraw, clear, emit) {
        if (redraw === void 0) { redraw = true; }
        if (clear === void 0) { clear = true; }
        if (emit === void 0) { emit = true; }
        if (clear)
            cds.selection_manager.clear();
        if (redraw)
            cds.change.emit();
        if (emit) {
            cds.data = cds.data;
            cds.properties.data.change.emit();
        }
    };
    EditToolView.prototype._drag_points = function (ev, renderers) {
        if (this._basepoint == null) {
            return;
        }
        ;
        var _a = this._basepoint, bx = _a[0], by = _a[1];
        for (var _i = 0, renderers_1 = renderers; _i < renderers_1.length; _i++) {
            var renderer = renderers_1[_i];
            var basepoint = this._map_drag(bx, by, renderer);
            var point = this._map_drag(ev.sx, ev.sy, renderer);
            if (point == null || basepoint == null) {
                continue;
            }
            var x = point[0], y = point[1];
            var px = basepoint[0], py = basepoint[1];
            var _b = [x - px, y - py], dx = _b[0], dy = _b[1];
            // Type once dataspecs are typed
            var glyph = renderer.glyph;
            var cds = renderer.data_source;
            var _c = [glyph.x.field, glyph.y.field], xkey = _c[0], ykey = _c[1];
            for (var _d = 0, _f = cds.selected.indices; _d < _f.length; _d++) {
                var index = _f[_d];
                if (xkey)
                    cds.data[xkey][index] += dx;
                if (ykey)
                    cds.data[ykey][index] += dy;
            }
            cds.change.emit();
        }
        this._basepoint = [ev.sx, ev.sy];
    };
    EditToolView.prototype._pad_empty_columns = function (cds, coord_columns) {
        // Pad ColumnDataSource non-coordinate columns with empty_value
        for (var _i = 0, _a = cds.columns(); _i < _a.length; _i++) {
            var column = _a[_i];
            if (!array_1.includes(coord_columns, column))
                cds.get_array(column).push(this.model.empty_value);
        }
    };
    EditToolView.prototype._select_event = function (ev, append, renderers) {
        // Process selection event on the supplied renderers and return selected renderers
        var frame = this.plot_model.frame;
        var sx = ev.sx, sy = ev.sy;
        if (!frame.bbox.contains(sx, sy)) {
            return [];
        }
        var geometry = {
            type: 'point',
            sx: sx,
            sy: sy,
        };
        var selected = [];
        for (var _i = 0, renderers_2 = renderers; _i < renderers_2.length; _i++) {
            var renderer = renderers_2[_i];
            var sm = renderer.get_selection_manager();
            var cds = renderer.data_source;
            var views = [this.plot_view.renderer_views[renderer.id]];
            var did_hit = sm.select(views, geometry, true, append);
            if (did_hit) {
                selected.push(renderer);
            }
            cds.properties.selected.change.emit();
        }
        return selected;
    };
    return EditToolView;
}(gesture_tool_1.GestureToolView));
exports.EditToolView = EditToolView;
var EditTool = /** @class */ (function (_super) {
    tslib_1.__extends(EditTool, _super);
    function EditTool(attrs) {
        return _super.call(this, attrs) || this;
    }
    EditTool.initClass = function () {
        this.prototype.type = "EditTool";
        this.define({
            custom_icon: [p.String,],
            custom_tooltip: [p.String,],
            empty_value: [p.Any,],
            renderers: [p.Array, []],
        });
    };
    Object.defineProperty(EditTool.prototype, "tooltip", {
        get: function () {
            return this.custom_tooltip || this.tool_name;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(EditTool.prototype, "computed_icon", {
        get: function () {
            return this.custom_icon || this.icon;
        },
        enumerable: true,
        configurable: true
    });
    return EditTool;
}(gesture_tool_1.GestureTool));
exports.EditTool = EditTool;
EditTool.initClass();
