"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gesture_tool_1 = require("./gesture_tool");
var graph_renderer_1 = require("../../renderers/graph_renderer");
var util_1 = require("../util");
var p = require("core/properties");
var dom_1 = require("core/dom");
var bokeh_events_1 = require("core/bokeh_events");
var SelectToolView = /** @class */ (function (_super) {
    tslib_1.__extends(SelectToolView, _super);
    function SelectToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(SelectToolView.prototype, "computed_renderers", {
        get: function () {
            var renderers = this.model.renderers;
            var all_renderers = this.plot_model.plot.renderers;
            var names = this.model.names;
            return util_1.compute_renderers(renderers, all_renderers, names);
        },
        enumerable: true,
        configurable: true
    });
    SelectToolView.prototype._computed_renderers_by_data_source = function () {
        var renderers_by_source = {};
        for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
            var r = _a[_i];
            var source_id = void 0;
            // XXX: needs typings for renderers
            if (r instanceof graph_renderer_1.GraphRenderer)
                source_id = r.node_renderer.data_source.id;
            else
                source_id = r.data_source.id;
            if (!(source_id in renderers_by_source))
                renderers_by_source[source_id] = [];
            renderers_by_source[source_id].push(r);
        }
        return renderers_by_source;
    };
    SelectToolView.prototype._keyup = function (ev) {
        if (ev.keyCode == dom_1.Keys.Esc) {
            for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
                var r = _a[_i];
                // XXX: needs typings for renderers
                var ds = r.data_source;
                var sm = ds.selection_manager;
                sm.clear();
            }
            this.plot_view.request_render();
        }
    };
    SelectToolView.prototype._select = function (geometry, final, append) {
        var renderers_by_source = this._computed_renderers_by_data_source();
        for (var id in renderers_by_source) {
            var renderers = renderers_by_source[id];
            var sm = renderers[0].get_selection_manager();
            var r_views = [];
            for (var _i = 0, renderers_1 = renderers; _i < renderers_1.length; _i++) {
                var r = renderers_1[_i];
                if (r.id in this.plot_view.renderer_views)
                    r_views.push(this.plot_view.renderer_views[r.id]);
            }
            sm.select(r_views, geometry, final, append);
        }
        // XXX: messed up class structure
        if (this.model.callback != null)
            this._emit_callback(geometry);
        this._emit_selection_event(geometry, final);
    };
    SelectToolView.prototype._emit_selection_event = function (geometry, final) {
        if (final === void 0) { final = true; }
        var xm = this.plot_model.frame.xscales['default'];
        var ym = this.plot_model.frame.yscales['default'];
        var g; // XXX: Geometry & something
        switch (geometry.type) {
            case 'point': {
                var sx = geometry.sx, sy = geometry.sy;
                var x = xm.invert(sx);
                var y = ym.invert(sy);
                g = tslib_1.__assign({}, geometry, { x: x, y: y });
                break;
            }
            case 'rect': {
                var sx0 = geometry.sx0, sx1 = geometry.sx1, sy0 = geometry.sy0, sy1 = geometry.sy1;
                var _a = xm.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
                var _b = ym.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
                g = tslib_1.__assign({}, geometry, { x0: x0, y0: y0, x1: x1, y1: y1 });
                break;
            }
            case 'poly': {
                var sx = geometry.sx, sy = geometry.sy;
                var x = xm.v_invert(sx);
                var y = ym.v_invert(sy);
                g = tslib_1.__assign({}, geometry, { x: x, y: y });
                break;
            }
            default:
                throw new Error("Unrecognized selection geometry type: '" + geometry.type + "'");
        }
        this.plot_model.plot.trigger_event(new bokeh_events_1.SelectionGeometry({ geometry: g, final: final }));
    };
    return SelectToolView;
}(gesture_tool_1.GestureToolView));
exports.SelectToolView = SelectToolView;
var SelectTool = /** @class */ (function (_super) {
    tslib_1.__extends(SelectTool, _super);
    function SelectTool(attrs) {
        return _super.call(this, attrs) || this;
    }
    SelectTool.initClass = function () {
        this.prototype.type = "SelectTool";
        this.define({
            renderers: [p.Any, 'auto'],
            names: [p.Array, []],
        });
    };
    return SelectTool;
}(gesture_tool_1.GestureTool));
exports.SelectTool = SelectTool;
SelectTool.initClass();
