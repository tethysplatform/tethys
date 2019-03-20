"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var types_1 = require("core/util/types");
var poly_tool_1 = require("./poly_tool");
var PolyEditToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PolyEditToolView, _super);
    function PolyEditToolView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._drawing = false;
        return _this;
    }
    PolyEditToolView.prototype._doubletap = function (ev) {
        if (!this.model.active) {
            return;
        }
        var point = this._map_drag(ev.sx, ev.sy, this.model.vertex_renderer);
        if (point == null) {
            return;
        }
        var x = point[0], y = point[1];
        // Perform hit testing
        var vertex_selected = this._select_event(ev, false, [this.model.vertex_renderer]);
        var point_cds = this.model.vertex_renderer.data_source;
        // Type once dataspecs are typed
        var point_glyph = this.model.vertex_renderer.glyph;
        var _a = [point_glyph.x.field, point_glyph.y.field], pxkey = _a[0], pykey = _a[1];
        if (vertex_selected.length && this._selected_renderer != null) {
            // Insert a new point after the selected vertex and enter draw mode
            var index = point_cds.selected.indices[0];
            if (this._drawing) {
                this._drawing = false;
                point_cds.selection_manager.clear();
            }
            else {
                point_cds.selected.indices = [index + 1];
                if (pxkey)
                    point_cds.get_array(pxkey).splice(index + 1, 0, x);
                if (pykey)
                    point_cds.get_array(pykey).splice(index + 1, 0, y);
                this._drawing = true;
            }
            point_cds.change.emit();
            this._emit_cds_changes(this._selected_renderer.data_source);
        }
        else {
            this._show_vertices(ev);
        }
    };
    PolyEditToolView.prototype._show_vertices = function (ev) {
        if (!this.model.active) {
            return;
        }
        var renderers = this._select_event(ev, false, this.model.renderers);
        if (!renderers.length) {
            this._set_vertices([], []);
            this._selected_renderer = null;
            this._drawing = false;
            return;
        }
        var renderer = renderers[0];
        var glyph = renderer.glyph;
        var cds = renderer.data_source;
        var index = cds.selected.indices[0];
        var _a = [glyph.xs.field, glyph.ys.field], xkey = _a[0], ykey = _a[1];
        var xs;
        var ys;
        if (xkey) {
            xs = cds.data[xkey][index];
            if (!types_1.isArray(xs))
                cds.data[xkey][index] = xs = Array.from(xs);
        }
        else {
            xs = glyph.xs.value;
        }
        if (ykey) {
            ys = cds.data[ykey][index];
            if (!types_1.isArray(ys))
                cds.data[ykey][index] = ys = Array.from(ys);
        }
        else {
            ys = glyph.ys.value;
        }
        this._selected_renderer = renderer;
        this._set_vertices(xs, ys);
    };
    PolyEditToolView.prototype._move = function (ev) {
        var _a;
        if (this._drawing && this._selected_renderer != null) {
            var renderer = this.model.vertex_renderer;
            var cds = renderer.data_source;
            var glyph = renderer.glyph;
            var point = this._map_drag(ev.sx, ev.sy, renderer);
            if (point == null) {
                return;
            }
            var x = point[0], y = point[1];
            var indices = cds.selected.indices;
            _a = this._snap_to_vertex(ev, x, y), x = _a[0], y = _a[1];
            cds.selected.indices = indices;
            var _b = [glyph.x.field, glyph.y.field], xkey = _b[0], ykey = _b[1];
            var index = indices[0];
            if (xkey)
                cds.data[xkey][index] = x;
            if (ykey)
                cds.data[ykey][index] = y;
            cds.change.emit();
            this._selected_renderer.data_source.change.emit();
        }
    };
    PolyEditToolView.prototype._tap = function (ev) {
        var _a;
        var renderer = this.model.vertex_renderer;
        var point = this._map_drag(ev.sx, ev.sy, renderer);
        if (point == null) {
            return;
        }
        else if (this._drawing && this._selected_renderer) {
            var x = point[0], y = point[1];
            var cds = renderer.data_source;
            // Type once dataspecs are typed
            var glyph = renderer.glyph;
            var _b = [glyph.x.field, glyph.y.field], xkey = _b[0], ykey = _b[1];
            var indices = cds.selected.indices;
            _a = this._snap_to_vertex(ev, x, y), x = _a[0], y = _a[1];
            var index = indices[0];
            cds.selected.indices = [index + 1];
            if (xkey) {
                var xs = cds.get_array(xkey);
                var nx = xs[index];
                xs[index] = x;
                xs.splice(index + 1, 0, nx);
            }
            if (ykey) {
                var ys = cds.get_array(ykey);
                var ny = ys[index];
                ys[index] = y;
                ys.splice(index + 1, 0, ny);
            }
            cds.change.emit();
            this._emit_cds_changes(this._selected_renderer.data_source, true, false, true);
            return;
        }
        var append = ev.shiftKey;
        this._select_event(ev, append, [renderer]);
        this._select_event(ev, append, this.model.renderers);
    };
    PolyEditToolView.prototype._remove_vertex = function () {
        if (!this._drawing || !this._selected_renderer) {
            return;
        }
        var renderer = this.model.vertex_renderer;
        var cds = renderer.data_source;
        // Type once dataspecs are typed
        var glyph = renderer.glyph;
        var index = cds.selected.indices[0];
        var _a = [glyph.x.field, glyph.y.field], xkey = _a[0], ykey = _a[1];
        if (xkey)
            cds.get_array(xkey).splice(index, 1);
        if (ykey)
            cds.get_array(ykey).splice(index, 1);
        cds.change.emit();
        this._emit_cds_changes(this._selected_renderer.data_source);
    };
    PolyEditToolView.prototype._pan_start = function (ev) {
        this._select_event(ev, true, [this.model.vertex_renderer]);
        this._basepoint = [ev.sx, ev.sy];
    };
    PolyEditToolView.prototype._pan = function (ev) {
        if (this._basepoint == null) {
            return;
        }
        this._drag_points(ev, [this.model.vertex_renderer]);
        if (this._selected_renderer) {
            this._selected_renderer.data_source.change.emit();
        }
    };
    PolyEditToolView.prototype._pan_end = function (ev) {
        if (this._basepoint == null) {
            return;
        }
        this._drag_points(ev, [this.model.vertex_renderer]);
        this._emit_cds_changes(this.model.vertex_renderer.data_source, false, true, true);
        if (this._selected_renderer) {
            this._emit_cds_changes(this._selected_renderer.data_source);
        }
        this._basepoint = null;
    };
    PolyEditToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        var renderers;
        if (this._selected_renderer) {
            renderers = [this.model.vertex_renderer];
        }
        else {
            renderers = this.model.renderers;
        }
        for (var _i = 0, renderers_1 = renderers; _i < renderers_1.length; _i++) {
            var renderer = renderers_1[_i];
            if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
                if (this._selected_renderer) {
                    this._emit_cds_changes(this._selected_renderer.data_source);
                }
            }
            else if (ev.keyCode == dom_1.Keys.Esc) {
                if (this._drawing) {
                    this._remove_vertex();
                    this._drawing = false;
                }
                else if (this._selected_renderer) {
                    this._hide_vertices();
                }
                renderer.data_source.selection_manager.clear();
            }
        }
    };
    PolyEditToolView.prototype.deactivate = function () {
        if (!this._selected_renderer) {
            return;
        }
        else if (this._drawing) {
            this._remove_vertex();
            this._drawing = false;
        }
        this._hide_vertices();
    };
    return PolyEditToolView;
}(poly_tool_1.PolyToolView));
exports.PolyEditToolView = PolyEditToolView;
var PolyEditTool = /** @class */ (function (_super) {
    tslib_1.__extends(PolyEditTool, _super);
    function PolyEditTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Poly Edit Tool";
        _this.icon = "bk-tool-icon-poly-edit";
        _this.event_type = ["tap", "pan", "move"];
        _this.default_order = 4;
        return _this;
    }
    PolyEditTool.initClass = function () {
        this.prototype.type = "PolyEditTool";
        this.prototype.default_view = PolyEditToolView;
    };
    return PolyEditTool;
}(poly_tool_1.PolyTool));
exports.PolyEditTool = PolyEditTool;
PolyEditTool.initClass();
