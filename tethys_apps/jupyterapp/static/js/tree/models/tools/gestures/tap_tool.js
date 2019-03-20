"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var select_tool_1 = require("./select_tool");
var p = require("core/properties");
var types_1 = require("core/util/types");
var TapToolView = /** @class */ (function (_super) {
    tslib_1.__extends(TapToolView, _super);
    function TapToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TapToolView.prototype._tap = function (ev) {
        var sx = ev.sx, sy = ev.sy;
        var geometry = {
            type: 'point',
            sx: sx,
            sy: sy,
        };
        var append = ev.shiftKey;
        this._select(geometry, true, append);
    };
    TapToolView.prototype._select = function (geometry, final, append) {
        var _this = this;
        var callback = this.model.callback;
        if (this.model.behavior == "select") {
            var renderers_by_source = this._computed_renderers_by_data_source();
            for (var id in renderers_by_source) {
                var renderers = renderers_by_source[id];
                var sm = renderers[0].get_selection_manager();
                var r_views = renderers.map(function (r) { return _this.plot_view.renderer_views[r.id]; });
                var did_hit = sm.select(r_views, geometry, final, append);
                if (did_hit && callback != null) {
                    var frame = this.plot_model.frame;
                    var xscale = frame.xscales[renderers[0].x_range_name];
                    var yscale = frame.yscales[renderers[0].y_range_name];
                    var x = xscale.invert(geometry.sx);
                    var y = yscale.invert(geometry.sy);
                    var g = tslib_1.__assign({}, geometry, { x: x, y: y });
                    var cb_data = { geometries: g, source: sm.source };
                    if (types_1.isFunction(callback))
                        callback(this, cb_data);
                    else
                        callback.execute(this, cb_data);
                }
            }
            this._emit_selection_event(geometry);
            this.plot_view.push_state('tap', { selection: this.plot_view.get_selection() });
        }
        else {
            for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
                var r = _a[_i];
                var sm = r.get_selection_manager();
                var did_hit = sm.inspect(this.plot_view.renderer_views[r.id], geometry);
                if (did_hit && callback != null) {
                    var frame = this.plot_model.frame;
                    var xscale = frame.xscales[r.x_range_name];
                    var yscale = frame.yscales[r.y_range_name];
                    var x = xscale.invert(geometry.sx);
                    var y = yscale.invert(geometry.sy);
                    var g = tslib_1.__assign({}, geometry, { x: x, y: y });
                    var cb_data = { geometries: g, source: sm.source };
                    if (types_1.isFunction(callback))
                        callback(this, cb_data);
                    else
                        callback.execute(this, cb_data);
                }
            }
        }
    };
    return TapToolView;
}(select_tool_1.SelectToolView));
exports.TapToolView = TapToolView;
var TapTool = /** @class */ (function (_super) {
    tslib_1.__extends(TapTool, _super);
    function TapTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Tap";
        _this.icon = "bk-tool-icon-tap-select";
        _this.event_type = "tap";
        _this.default_order = 10;
        return _this;
    }
    TapTool.initClass = function () {
        this.prototype.type = "TapTool";
        this.prototype.default_view = TapToolView;
        this.define({
            behavior: [p.String, "select"],
            callback: [p.Any],
        });
    };
    return TapTool;
}(select_tool_1.SelectTool));
exports.TapTool = TapTool;
TapTool.initClass();
