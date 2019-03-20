"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var types_1 = require("core/util/types");
var edit_tool_1 = require("./edit_tool");
var PolyToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PolyToolView, _super);
    function PolyToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PolyToolView.prototype._set_vertices = function (xs, ys) {
        var point_glyph = this.model.vertex_renderer.glyph;
        var point_cds = this.model.vertex_renderer.data_source;
        var _a = [point_glyph.x.field, point_glyph.y.field], pxkey = _a[0], pykey = _a[1];
        if (pxkey) {
            if (types_1.isArray(xs))
                point_cds.data[pxkey] = xs;
            else
                point_glyph.x = { value: xs };
        }
        if (pykey) {
            if (types_1.isArray(ys))
                point_cds.data[pykey] = ys;
            else
                point_glyph.y = { value: ys };
        }
        this._emit_cds_changes(point_cds, true, true, false);
    };
    PolyToolView.prototype._hide_vertices = function () {
        this._set_vertices([], []);
    };
    PolyToolView.prototype._snap_to_vertex = function (ev, x, y) {
        if (this.model.vertex_renderer) {
            // If an existing vertex is hit snap to it
            var vertex_selected = this._select_event(ev, false, [this.model.vertex_renderer]);
            var point_ds = this.model.vertex_renderer.data_source;
            // Type once dataspecs are typed
            var point_glyph = this.model.vertex_renderer.glyph;
            var _a = [point_glyph.x.field, point_glyph.y.field], pxkey = _a[0], pykey = _a[1];
            if (vertex_selected.length) {
                var index = point_ds.selected.indices[0];
                if (pxkey)
                    x = point_ds.data[pxkey][index];
                if (pykey)
                    y = point_ds.data[pykey][index];
                point_ds.selection_manager.clear();
            }
        }
        return [x, y];
    };
    return PolyToolView;
}(edit_tool_1.EditToolView));
exports.PolyToolView = PolyToolView;
var PolyTool = /** @class */ (function (_super) {
    tslib_1.__extends(PolyTool, _super);
    function PolyTool(attrs) {
        return _super.call(this, attrs) || this;
    }
    PolyTool.initClass = function () {
        this.prototype.type = "PolyTool";
        this.prototype.default_view = PolyToolView;
        this.define({
            vertex_renderer: [p.Instance],
        });
    };
    return PolyTool;
}(edit_tool_1.EditTool));
exports.PolyTool = PolyTool;
PolyTool.initClass();
