"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var types_1 = require("core/util/types");
var poly_tool_1 = require("./poly_tool");
var PolyDrawToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PolyDrawToolView, _super);
    function PolyDrawToolView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._drawing = false;
        _this._initialized = false;
        return _this;
    }
    PolyDrawToolView.prototype._tap = function (ev) {
        if (this._drawing)
            this._draw(ev, 'add', true);
        else
            this._select_event(ev, ev.shiftKey, this.model.renderers);
    };
    PolyDrawToolView.prototype._draw = function (ev, mode, emit) {
        if (emit === void 0) { emit = false; }
        var _a;
        var renderer = this.model.renderers[0];
        var point = this._map_drag(ev.sx, ev.sy, renderer);
        if (!this._initialized)
            this.activate(); // Ensure that activate has been called
        if (point == null) {
            return;
        }
        var x = point[0], y = point[1];
        _a = this._snap_to_vertex(ev, x, y), x = _a[0], y = _a[1];
        var cds = renderer.data_source;
        var glyph = renderer.glyph;
        var _b = [glyph.xs.field, glyph.ys.field], xkey = _b[0], ykey = _b[1];
        if (mode == 'new') {
            this._pop_glyphs(cds, this.model.num_objects);
            if (xkey)
                cds.get_array(xkey).push([x, x]);
            if (ykey)
                cds.get_array(ykey).push([y, y]);
            this._pad_empty_columns(cds, [xkey, ykey]);
        }
        else if (mode == 'edit') {
            if (xkey) {
                var xs = cds.data[xkey][cds.data[xkey].length - 1];
                xs[xs.length - 1] = x;
            }
            if (ykey) {
                var ys = cds.data[ykey][cds.data[ykey].length - 1];
                ys[ys.length - 1] = y;
            }
        }
        else if (mode == 'add') {
            if (xkey) {
                var xidx = cds.data[xkey].length - 1;
                var xs = cds.get_array(xkey)[xidx];
                var nx = xs[xs.length - 1];
                xs[xs.length - 1] = x;
                if (!types_1.isArray(xs)) {
                    xs = Array.from(xs);
                    cds.data[xkey][xidx] = xs;
                }
                xs.push(nx);
            }
            if (ykey) {
                var yidx = cds.data[ykey].length - 1;
                var ys = cds.get_array(ykey)[yidx];
                var ny = ys[ys.length - 1];
                ys[ys.length - 1] = y;
                if (!types_1.isArray(ys)) {
                    ys = Array.from(ys);
                    cds.data[ykey][yidx] = ys;
                }
                ys.push(ny);
            }
        }
        this._emit_cds_changes(cds, true, false, emit);
    };
    PolyDrawToolView.prototype._show_vertices = function () {
        var xs = [];
        var ys = [];
        for (var i = 0; i < this.model.renderers.length; i++) {
            var renderer = this.model.renderers[i];
            var cds = renderer.data_source;
            var glyph = renderer.glyph;
            var _a = [glyph.xs.field, glyph.ys.field], xkey = _a[0], ykey = _a[1];
            if (xkey) {
                for (var _i = 0, _b = cds.get_array(xkey); _i < _b.length; _i++) {
                    var array = _b[_i];
                    Array.prototype.push.apply(xs, array);
                }
            }
            if (ykey) {
                for (var _c = 0, _d = cds.get_array(ykey); _c < _d.length; _c++) {
                    var array = _d[_c];
                    Array.prototype.push.apply(ys, array);
                }
            }
            if (this._drawing && (i == (this.model.renderers.length - 1))) {
                // Skip currently drawn vertex
                xs.splice(xs.length - 1, 1);
                ys.splice(ys.length - 1, 1);
            }
        }
        this._set_vertices(xs, ys);
    };
    PolyDrawToolView.prototype._doubletap = function (ev) {
        if (!this.model.active) {
            return;
        }
        if (this._drawing) {
            this._drawing = false;
            this._draw(ev, 'edit', true);
        }
        else {
            this._drawing = true;
            this._draw(ev, 'new', true);
        }
    };
    PolyDrawToolView.prototype._move = function (ev) {
        if (this._drawing) {
            this._draw(ev, 'edit');
        }
    };
    PolyDrawToolView.prototype._remove = function () {
        var renderer = this.model.renderers[0];
        var cds = renderer.data_source;
        var glyph = renderer.glyph;
        var _a = [glyph.xs.field, glyph.ys.field], xkey = _a[0], ykey = _a[1];
        if (xkey) {
            var xidx = cds.data[xkey].length - 1;
            var xs = cds.get_array(xkey)[xidx];
            xs.splice(xs.length - 1, 1);
        }
        if (ykey) {
            var yidx = cds.data[ykey].length - 1;
            var ys = cds.get_array(ykey)[yidx];
            ys.splice(ys.length - 1, 1);
        }
        this._emit_cds_changes(cds);
    };
    PolyDrawToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
            }
            else if (ev.keyCode == dom_1.Keys.Esc) {
                if (this._drawing) {
                    this._remove();
                    this._drawing = false;
                }
                renderer.data_source.selection_manager.clear();
            }
        }
    };
    PolyDrawToolView.prototype._pan_start = function (ev) {
        if (!this.model.drag) {
            return;
        }
        this._select_event(ev, true, this.model.renderers);
        this._basepoint = [ev.sx, ev.sy];
    };
    PolyDrawToolView.prototype._pan = function (ev) {
        if (this._basepoint == null || !this.model.drag) {
            return;
        }
        var _a = this._basepoint, bx = _a[0], by = _a[1];
        // Process polygon/line dragging
        for (var _i = 0, _b = this.model.renderers; _i < _b.length; _i++) {
            var renderer = _b[_i];
            var basepoint = this._map_drag(bx, by, renderer);
            var point = this._map_drag(ev.sx, ev.sy, renderer);
            if (point == null || basepoint == null) {
                continue;
            }
            var cds = renderer.data_source;
            // Type once dataspecs are typed
            var glyph = renderer.glyph;
            var _c = [glyph.xs.field, glyph.ys.field], xkey = _c[0], ykey = _c[1];
            if (!xkey && !ykey) {
                continue;
            }
            var x = point[0], y = point[1];
            var px = basepoint[0], py = basepoint[1];
            var _d = [x - px, y - py], dx = _d[0], dy = _d[1];
            for (var _e = 0, _f = cds.selected.indices; _e < _f.length; _e++) {
                var index = _f[_e];
                var length_1 = void 0, xs = void 0, ys = void 0;
                if (xkey)
                    xs = cds.data[xkey][index];
                if (ykey) {
                    ys = cds.data[ykey][index];
                    length_1 = ys.length;
                }
                else {
                    length_1 = xs.length;
                }
                for (var i = 0; i < length_1; i++) {
                    if (xs) {
                        xs[i] += dx;
                    }
                    if (ys) {
                        ys[i] += dy;
                    }
                }
            }
            cds.change.emit();
        }
        this._basepoint = [ev.sx, ev.sy];
    };
    PolyDrawToolView.prototype._pan_end = function (ev) {
        if (!this.model.drag) {
            return;
        }
        this._pan(ev);
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            this._emit_cds_changes(renderer.data_source);
        }
        this._basepoint = null;
    };
    PolyDrawToolView.prototype.activate = function () {
        var _this = this;
        if (!this.model.vertex_renderer || !this.model.active) {
            return;
        }
        this._show_vertices();
        if (!this._initialized) {
            for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
                var renderer = _a[_i];
                var cds = renderer.data_source;
                cds.connect(cds.properties.data.change, function () { return _this._show_vertices(); });
            }
        }
        this._initialized = true;
    };
    PolyDrawToolView.prototype.deactivate = function () {
        if (this._drawing) {
            this._remove();
            this._drawing = false;
        }
        if (this.model.vertex_renderer)
            this._hide_vertices();
    };
    return PolyDrawToolView;
}(poly_tool_1.PolyToolView));
exports.PolyDrawToolView = PolyDrawToolView;
var PolyDrawTool = /** @class */ (function (_super) {
    tslib_1.__extends(PolyDrawTool, _super);
    function PolyDrawTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Polygon Draw Tool";
        _this.icon = "bk-tool-icon-poly-draw";
        _this.event_type = ["pan", "tap", "move"];
        _this.default_order = 3;
        return _this;
    }
    PolyDrawTool.initClass = function () {
        this.prototype.type = "PolyDrawTool";
        this.prototype.default_view = PolyDrawToolView;
        this.define({
            drag: [p.Bool, true],
            num_objects: [p.Int, 0],
        });
    };
    return PolyDrawTool;
}(poly_tool_1.PolyTool));
exports.PolyDrawTool = PolyDrawTool;
PolyDrawTool.initClass();
