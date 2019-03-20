"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var select_tool_1 = require("./select_tool");
var poly_annotation_1 = require("../../annotations/poly_annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
var array_1 = require("core/util/array");
var PolySelectToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PolySelectToolView, _super);
    function PolySelectToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PolySelectToolView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.data = { sx: [], sy: [] };
    };
    PolySelectToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.active.change, function () { return _this._active_change(); });
    };
    PolySelectToolView.prototype._active_change = function () {
        if (!this.model.active)
            this._clear_data();
    };
    PolySelectToolView.prototype._keyup = function (ev) {
        if (ev.keyCode == dom_1.Keys.Enter)
            this._clear_data();
    };
    PolySelectToolView.prototype._doubletap = function (ev) {
        var append = ev.shiftKey;
        this._do_select(this.data.sx, this.data.sy, true, append);
        this.plot_view.push_state('poly_select', { selection: this.plot_view.get_selection() });
        this._clear_data();
    };
    PolySelectToolView.prototype._clear_data = function () {
        this.data = { sx: [], sy: [] };
        this.model.overlay.update({ xs: [], ys: [] });
    };
    PolySelectToolView.prototype._tap = function (ev) {
        var sx = ev.sx, sy = ev.sy;
        var frame = this.plot_model.frame;
        if (!frame.bbox.contains(sx, sy))
            return;
        this.data.sx.push(sx);
        this.data.sy.push(sy);
        this.model.overlay.update({ xs: array_1.copy(this.data.sx), ys: array_1.copy(this.data.sy) });
    };
    PolySelectToolView.prototype._do_select = function (sx, sy, final, append) {
        var geometry = {
            type: 'poly',
            sx: sx,
            sy: sy,
        };
        this._select(geometry, final, append);
    };
    PolySelectToolView.prototype._emit_callback = function (geometry) {
        var r = this.computed_renderers[0];
        var frame = this.plot_model.frame;
        var xscale = frame.xscales[r.x_range_name];
        var yscale = frame.yscales[r.y_range_name];
        var x = xscale.v_invert(geometry.sx);
        var y = yscale.v_invert(geometry.sy);
        var g = tslib_1.__assign({ x: x, y: y }, geometry);
        this.model.callback.execute(this.model, { geometry: g });
    };
    return PolySelectToolView;
}(select_tool_1.SelectToolView));
exports.PolySelectToolView = PolySelectToolView;
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
var PolySelectTool = /** @class */ (function (_super) {
    tslib_1.__extends(PolySelectTool, _super);
    function PolySelectTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Poly Select";
        _this.icon = "bk-tool-icon-polygon-select";
        _this.event_type = "tap";
        _this.default_order = 11;
        return _this;
    }
    PolySelectTool.initClass = function () {
        this.prototype.type = "PolySelectTool";
        this.prototype.default_view = PolySelectToolView;
        this.define({
            callback: [p.Instance],
            overlay: [p.Instance, DEFAULT_POLY_OVERLAY],
        });
    };
    return PolySelectTool;
}(select_tool_1.SelectTool));
exports.PolySelectTool = PolySelectTool;
PolySelectTool.initClass();
