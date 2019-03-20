"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var select_tool_1 = require("./select_tool");
var box_annotation_1 = require("../../annotations/box_annotation");
var p = require("core/properties");
var BoxSelectToolView = /** @class */ (function (_super) {
    tslib_1.__extends(BoxSelectToolView, _super);
    function BoxSelectToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BoxSelectToolView.prototype._compute_limits = function (curpoint) {
        var frame = this.plot_model.frame;
        var dims = this.model.dimensions;
        var base_point = this._base_point;
        if (this.model.origin == "center") {
            var cx = base_point[0], cy = base_point[1];
            var dx = curpoint[0], dy = curpoint[1];
            base_point = [cx - (dx - cx), cy - (dy - cy)];
        }
        return this.model._get_dim_limits(base_point, curpoint, frame, dims);
    };
    BoxSelectToolView.prototype._pan_start = function (ev) {
        var sx = ev.sx, sy = ev.sy;
        this._base_point = [sx, sy];
    };
    BoxSelectToolView.prototype._pan = function (ev) {
        var sx = ev.sx, sy = ev.sy;
        var curpoint = [sx, sy];
        var _a = this._compute_limits(curpoint), sxlim = _a[0], sylim = _a[1];
        this.model.overlay.update({ left: sxlim[0], right: sxlim[1], top: sylim[0], bottom: sylim[1] });
        if (this.model.select_every_mousemove) {
            var append = ev.shiftKey;
            this._do_select(sxlim, sylim, false, append);
        }
    };
    BoxSelectToolView.prototype._pan_end = function (ev) {
        var sx = ev.sx, sy = ev.sy;
        var curpoint = [sx, sy];
        var _a = this._compute_limits(curpoint), sxlim = _a[0], sylim = _a[1];
        var append = ev.shiftKey;
        this._do_select(sxlim, sylim, true, append);
        this.model.overlay.update({ left: null, right: null, top: null, bottom: null });
        this._base_point = null;
        this.plot_view.push_state('box_select', { selection: this.plot_view.get_selection() });
    };
    BoxSelectToolView.prototype._do_select = function (_a, _b, final, append) {
        var sx0 = _a[0], sx1 = _a[1];
        var sy0 = _b[0], sy1 = _b[1];
        if (append === void 0) { append = false; }
        var geometry = {
            type: 'rect',
            sx0: sx0,
            sx1: sx1,
            sy0: sy0,
            sy1: sy1,
        };
        this._select(geometry, final, append);
    };
    BoxSelectToolView.prototype._emit_callback = function (geometry) {
        var r = this.computed_renderers[0];
        var frame = this.plot_model.frame;
        var xscale = frame.xscales[r.x_range_name];
        var yscale = frame.yscales[r.y_range_name];
        var sx0 = geometry.sx0, sx1 = geometry.sx1, sy0 = geometry.sy0, sy1 = geometry.sy1;
        var _a = xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var _b = yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var g = tslib_1.__assign({ x0: x0, y0: y0, x1: x1, y1: y1 }, geometry);
        this.model.callback.execute(this.model, { geometry: g });
    };
    return BoxSelectToolView;
}(select_tool_1.SelectToolView));
exports.BoxSelectToolView = BoxSelectToolView;
var DEFAULT_BOX_OVERLAY = function () {
    return new box_annotation_1.BoxAnnotation({
        level: "overlay",
        render_mode: "css",
        top_units: "screen",
        left_units: "screen",
        bottom_units: "screen",
        right_units: "screen",
        fill_color: { value: "lightgrey" },
        fill_alpha: { value: 0.5 },
        line_color: { value: "black" },
        line_alpha: { value: 1.0 },
        line_width: { value: 2 },
        line_dash: { value: [4, 4] },
    });
};
var BoxSelectTool = /** @class */ (function (_super) {
    tslib_1.__extends(BoxSelectTool, _super);
    function BoxSelectTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Box Select";
        _this.icon = "bk-tool-icon-box-select";
        _this.event_type = "pan";
        _this.default_order = 30;
        return _this;
    }
    BoxSelectTool.initClass = function () {
        this.prototype.type = "BoxSelectTool";
        this.prototype.default_view = BoxSelectToolView;
        this.define({
            dimensions: [p.Dimensions, "both"],
            select_every_mousemove: [p.Bool, false],
            callback: [p.Instance],
            overlay: [p.Instance, DEFAULT_BOX_OVERLAY],
            origin: [p.String, "corner"],
        });
    };
    Object.defineProperty(BoxSelectTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    return BoxSelectTool;
}(select_tool_1.SelectTool));
exports.BoxSelectTool = BoxSelectTool;
BoxSelectTool.initClass();
