"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var types_1 = require("core/util/types");
var edit_tool_1 = require("./edit_tool");
var FreehandDrawToolView = /** @class */ (function (_super) {
    tslib_1.__extends(FreehandDrawToolView, _super);
    function FreehandDrawToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    FreehandDrawToolView.prototype._draw = function (ev, mode, emit) {
        if (emit === void 0) { emit = false; }
        if (!this.model.active) {
            return;
        }
        var renderer = this.model.renderers[0];
        var point = this._map_drag(ev.sx, ev.sy, renderer);
        if (point == null) {
            return;
        }
        var x = point[0], y = point[1];
        var cds = renderer.data_source;
        var glyph = renderer.glyph;
        var _a = [glyph.xs.field, glyph.ys.field], xkey = _a[0], ykey = _a[1];
        if (mode == 'new') {
            this._pop_glyphs(cds, this.model.num_objects);
            if (xkey)
                cds.get_array(xkey).push([x]);
            if (ykey)
                cds.get_array(ykey).push([y]);
            this._pad_empty_columns(cds, [xkey, ykey]);
        }
        else if (mode == 'add') {
            if (xkey) {
                var xidx = cds.data[xkey].length - 1;
                var xs = cds.get_array(xkey)[xidx];
                if (!types_1.isArray(xs)) {
                    xs = Array.from(xs);
                    cds.data[xkey][xidx] = xs;
                }
                xs.push(x);
            }
            if (ykey) {
                var yidx = cds.data[ykey].length - 1;
                var ys = cds.get_array(ykey)[yidx];
                if (!types_1.isArray(ys)) {
                    ys = Array.from(ys);
                    cds.data[ykey][yidx] = ys;
                }
                ys.push(y);
            }
        }
        this._emit_cds_changes(cds, true, true, emit);
    };
    FreehandDrawToolView.prototype._pan_start = function (ev) {
        this._draw(ev, 'new');
    };
    FreehandDrawToolView.prototype._pan = function (ev) {
        this._draw(ev, 'add');
    };
    FreehandDrawToolView.prototype._pan_end = function (ev) {
        this._draw(ev, 'add', true);
    };
    FreehandDrawToolView.prototype._tap = function (ev) {
        this._select_event(ev, ev.shiftKey, this.model.renderers);
    };
    FreehandDrawToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (ev.keyCode === dom_1.Keys.Esc) {
                renderer.data_source.selection_manager.clear();
            }
            else if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
            }
        }
    };
    return FreehandDrawToolView;
}(edit_tool_1.EditToolView));
exports.FreehandDrawToolView = FreehandDrawToolView;
var FreehandDrawTool = /** @class */ (function (_super) {
    tslib_1.__extends(FreehandDrawTool, _super);
    function FreehandDrawTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Freehand Draw Tool";
        _this.icon = "bk-tool-icon-freehand-draw";
        _this.event_type = ["pan", "tap"];
        _this.default_order = 3;
        return _this;
    }
    FreehandDrawTool.initClass = function () {
        this.prototype.type = "FreehandDrawTool";
        this.prototype.default_view = FreehandDrawToolView;
        this.define({
            num_objects: [p.Int, 0],
        });
    };
    return FreehandDrawTool;
}(edit_tool_1.EditTool));
exports.FreehandDrawTool = FreehandDrawTool;
FreehandDrawTool.initClass();
