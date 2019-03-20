"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var select_tool_1 = require("./select_tool");
var poly_annotation_1 = require("../../annotations/poly_annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
var LassoSelectToolView = /** @class */ (function (_super) {
    tslib_1.__extends(LassoSelectToolView, _super);
    function LassoSelectToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LassoSelectToolView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.data = null;
    };
    LassoSelectToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.active.change, function () { return _this._active_change(); });
    };
    LassoSelectToolView.prototype._active_change = function () {
        if (!this.model.active)
            this._clear_overlay();
    };
    LassoSelectToolView.prototype._keyup = function (ev) {
        if (ev.keyCode == dom_1.Keys.Enter)
            this._clear_overlay();
    };
    LassoSelectToolView.prototype._pan_start = function (ev) {
        var sx = ev.sx, sy = ev.sy;
        this.data = { sx: [sx], sy: [sy] };
    };
    LassoSelectToolView.prototype._pan = function (ev) {
        var _sx = ev.sx, _sy = ev.sy;
        var _a = this.plot_model.frame.bbox.clip(_sx, _sy), sx = _a[0], sy = _a[1];
        this.data.sx.push(sx);
        this.data.sy.push(sy);
        var overlay = this.model.overlay;
        overlay.update({ xs: this.data.sx, ys: this.data.sy });
        if (this.model.select_every_mousemove) {
            var append = ev.shiftKey;
            this._do_select(this.data.sx, this.data.sy, false, append);
        }
    };
    LassoSelectToolView.prototype._pan_end = function (ev) {
        this._clear_overlay();
        var append = ev.shiftKey;
        this._do_select(this.data.sx, this.data.sy, true, append);
        this.plot_view.push_state('lasso_select', { selection: this.plot_view.get_selection() });
    };
    LassoSelectToolView.prototype._clear_overlay = function () {
        this.model.overlay.update({ xs: [], ys: [] });
    };
    LassoSelectToolView.prototype._do_select = function (sx, sy, final, append) {
        var geometry = {
            type: 'poly',
            sx: sx,
            sy: sy,
        };
        this._select(geometry, final, append);
    };
    LassoSelectToolView.prototype._emit_callback = function (geometry) {
        var r = this.computed_renderers[0];
        var frame = this.plot_model.frame;
        var xscale = frame.xscales[r.x_range_name];
        var yscale = frame.yscales[r.y_range_name];
        var x = xscale.v_invert(geometry.sx);
        var y = yscale.v_invert(geometry.sy);
        var g = tslib_1.__assign({ x: x, y: y }, geometry);
        this.model.callback.execute(this.model, { geometry: g });
    };
    return LassoSelectToolView;
}(select_tool_1.SelectToolView));
exports.LassoSelectToolView = LassoSelectToolView;
var DEFAULT_POLY_OVERLAY = function () {
    return new poly_annotation_1.PolyAnnotation({
        level: "overlay",
        xs_units: "screen",
        ys_units: "screen",
        fill_color: { value: "lightgrey" },
        fill_alpha: { value: 0.5 },
        line_color: { value: "black" },
        line_alpha: { value: 1.0 },
        line_width: { value: 2 },
        line_dash: { value: [4, 4] },
    });
};
var LassoSelectTool = /** @class */ (function (_super) {
    tslib_1.__extends(LassoSelectTool, _super);
    function LassoSelectTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Lasso Select";
        _this.icon = "bk-tool-icon-lasso-select";
        _this.event_type = "pan";
        _this.default_order = 12;
        return _this;
    }
    LassoSelectTool.initClass = function () {
        this.prototype.type = "LassoSelectTool";
        this.prototype.default_view = LassoSelectToolView;
        this.define({
            select_every_mousemove: [p.Bool, true],
            callback: [p.Instance],
            overlay: [p.Instance, DEFAULT_POLY_OVERLAY],
        });
    };
    return LassoSelectTool;
}(select_tool_1.SelectTool));
exports.LassoSelectTool = LassoSelectTool;
LassoSelectTool.initClass();
