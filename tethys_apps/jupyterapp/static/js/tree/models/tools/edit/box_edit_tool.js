"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var edit_tool_1 = require("./edit_tool");
var BoxEditToolView = /** @class */ (function (_super) {
    tslib_1.__extends(BoxEditToolView, _super);
    function BoxEditToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BoxEditToolView.prototype._tap = function (ev) {
        if ((this._draw_basepoint != null) || (this._basepoint != null)) {
            return;
        }
        var append = ev.shiftKey;
        this._select_event(ev, append, this.model.renderers);
    };
    BoxEditToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
            }
            else if (ev.keyCode == dom_1.Keys.Esc) {
                // Type properly once selection_manager is typed
                var cds = renderer.data_source;
                cds.selection_manager.clear();
            }
        }
    };
    BoxEditToolView.prototype._set_extent = function (_a, _b, append, emit) {
        var sx0 = _a[0], sx1 = _a[1];
        var sy0 = _b[0], sy1 = _b[1];
        if (emit === void 0) { emit = false; }
        var renderer = this.model.renderers[0];
        var frame = this.plot_model.frame;
        // Type once dataspecs are typed
        var glyph = renderer.glyph;
        var cds = renderer.data_source;
        var xscale = frame.xscales[renderer.x_range_name];
        var yscale = frame.yscales[renderer.y_range_name];
        var _c = xscale.r_invert(sx0, sx1), x0 = _c[0], x1 = _c[1];
        var _d = yscale.r_invert(sy0, sy1), y0 = _d[0], y1 = _d[1];
        var _e = [(x0 + x1) / 2., (y0 + y1) / 2.], x = _e[0], y = _e[1];
        var _f = [x1 - x0, y1 - y0], w = _f[0], h = _f[1];
        var _g = [glyph.x.field, glyph.y.field], xkey = _g[0], ykey = _g[1];
        var _h = [glyph.width.field, glyph.height.field], wkey = _h[0], hkey = _h[1];
        if (append) {
            this._pop_glyphs(cds, this.model.num_objects);
            if (xkey)
                cds.get_array(xkey).push(x);
            if (ykey)
                cds.get_array(ykey).push(y);
            if (wkey)
                cds.get_array(wkey).push(w);
            if (hkey)
                cds.get_array(hkey).push(h);
            this._pad_empty_columns(cds, [xkey, ykey, wkey, hkey]);
        }
        else {
            var index = cds.data[xkey].length - 1;
            if (xkey)
                cds.data[xkey][index] = x;
            if (ykey)
                cds.data[ykey][index] = y;
            if (wkey)
                cds.data[wkey][index] = w;
            if (hkey)
                cds.data[hkey][index] = h;
        }
        this._emit_cds_changes(cds, true, false, emit);
    };
    BoxEditToolView.prototype._update_box = function (ev, append, emit) {
        if (append === void 0) { append = false; }
        if (emit === void 0) { emit = false; }
        if (this._draw_basepoint == null) {
            return;
        }
        var curpoint = [ev.sx, ev.sy];
        var frame = this.plot_model.frame;
        var dims = this.model.dimensions;
        var limits = this.model._get_dim_limits(this._draw_basepoint, curpoint, frame, dims);
        if (limits != null) {
            var sxlim = limits[0], sylim = limits[1];
            this._set_extent(sxlim, sylim, append, emit);
        }
    };
    BoxEditToolView.prototype._doubletap = function (ev) {
        if (!this.model.active) {
            return;
        }
        if (this._draw_basepoint != null) {
            this._update_box(ev, false, true);
            this._draw_basepoint = null;
        }
        else {
            this._draw_basepoint = [ev.sx, ev.sy];
            this._select_event(ev, true, this.model.renderers);
            this._update_box(ev, true, false);
        }
    };
    BoxEditToolView.prototype._move = function (ev) {
        this._update_box(ev, false, false);
    };
    BoxEditToolView.prototype._pan_start = function (ev) {
        if (ev.shiftKey) {
            if (this._draw_basepoint != null) {
                return;
            }
            this._draw_basepoint = [ev.sx, ev.sy];
            this._update_box(ev, true, false);
        }
        else {
            if (this._basepoint != null) {
                return;
            }
            this._select_event(ev, true, this.model.renderers);
            this._basepoint = [ev.sx, ev.sy];
        }
    };
    BoxEditToolView.prototype._pan = function (ev, append, emit) {
        if (append === void 0) { append = false; }
        if (emit === void 0) { emit = false; }
        if (ev.shiftKey) {
            if (this._draw_basepoint == null) {
                return;
            }
            this._update_box(ev, append, emit);
        }
        else {
            if (this._basepoint == null) {
                return;
            }
            this._drag_points(ev, this.model.renderers);
        }
    };
    BoxEditToolView.prototype._pan_end = function (ev) {
        this._pan(ev, false, true);
        if (ev.shiftKey) {
            this._draw_basepoint = null;
        }
        else {
            this._basepoint = null;
            for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
                var renderer = _a[_i];
                this._emit_cds_changes(renderer.data_source, false, true, true);
            }
        }
    };
    return BoxEditToolView;
}(edit_tool_1.EditToolView));
exports.BoxEditToolView = BoxEditToolView;
var BoxEditTool = /** @class */ (function (_super) {
    tslib_1.__extends(BoxEditTool, _super);
    function BoxEditTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Box Edit Tool";
        _this.icon = "bk-tool-icon-box-edit";
        _this.event_type = ["tap", "pan", "move"];
        _this.default_order = 1;
        return _this;
    }
    BoxEditTool.initClass = function () {
        this.prototype.type = "BoxEditTool";
        this.prototype.default_view = BoxEditToolView;
        this.define({
            dimensions: [p.Dimensions, "both"],
            num_objects: [p.Int, 0],
        });
    };
    return BoxEditTool;
}(edit_tool_1.EditTool));
exports.BoxEditTool = BoxEditTool;
BoxEditTool.initClass();
