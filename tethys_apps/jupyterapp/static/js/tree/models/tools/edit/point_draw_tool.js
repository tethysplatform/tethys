"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var edit_tool_1 = require("./edit_tool");
var PointDrawToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PointDrawToolView, _super);
    function PointDrawToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PointDrawToolView.prototype._tap = function (ev) {
        var append = ev.shiftKey;
        var renderers = this._select_event(ev, append, this.model.renderers);
        if (renderers.length || !this.model.add) {
            return;
        }
        var renderer = this.model.renderers[0];
        var point = this._map_drag(ev.sx, ev.sy, renderer);
        if (point == null) {
            return;
        }
        // Type once dataspecs are typed
        var glyph = renderer.glyph;
        var cds = renderer.data_source;
        var _a = [glyph.x.field, glyph.y.field], xkey = _a[0], ykey = _a[1];
        var x = point[0], y = point[1];
        this._pop_glyphs(cds, this.model.num_objects);
        if (xkey)
            cds.get_array(xkey).push(x);
        if (ykey)
            cds.get_array(ykey).push(y);
        this._pad_empty_columns(cds, [xkey, ykey]);
        cds.change.emit();
        cds.data = cds.data;
        cds.properties.data.change.emit();
    };
    PointDrawToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
            }
            else if (ev.keyCode == dom_1.Keys.Esc) {
                renderer.data_source.selection_manager.clear();
            }
        }
    };
    PointDrawToolView.prototype._pan_start = function (ev) {
        if (!this.model.drag) {
            return;
        }
        this._select_event(ev, true, this.model.renderers);
        this._basepoint = [ev.sx, ev.sy];
    };
    PointDrawToolView.prototype._pan = function (ev) {
        if (!this.model.drag || this._basepoint == null) {
            return;
        }
        this._drag_points(ev, this.model.renderers);
    };
    PointDrawToolView.prototype._pan_end = function (ev) {
        if (!this.model.drag) {
            return;
        }
        this._pan(ev);
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            this._emit_cds_changes(renderer.data_source, false, true, true);
        }
        this._basepoint = null;
    };
    return PointDrawToolView;
}(edit_tool_1.EditToolView));
exports.PointDrawToolView = PointDrawToolView;
var PointDrawTool = /** @class */ (function (_super) {
    tslib_1.__extends(PointDrawTool, _super);
    function PointDrawTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Point Draw Tool";
        _this.icon = "bk-tool-icon-point-draw";
        _this.event_type = ["tap", "pan", "move"];
        _this.default_order = 2;
        return _this;
    }
    PointDrawTool.initClass = function () {
        this.prototype.type = "PointDrawTool";
        this.prototype.default_view = PointDrawToolView;
        this.define({
            add: [p.Bool, true],
            drag: [p.Bool, true],
            num_objects: [p.Int, 0],
        });
    };
    return PointDrawTool;
}(edit_tool_1.EditTool));
exports.PointDrawTool = PointDrawTool;
PointDrawTool.initClass();
