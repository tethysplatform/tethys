"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gesture_tool_1 = require("./gesture_tool");
var box_annotation_1 = require("../../annotations/box_annotation");
var p = require("core/properties");
var BoxZoomToolView = /** @class */ (function (_super) {
    tslib_1.__extends(BoxZoomToolView, _super);
    function BoxZoomToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BoxZoomToolView.prototype._match_aspect = function (base_point, curpoint, frame) {
        // aspect ratio of plot frame
        var a = frame.bbox.aspect;
        var hend = frame.bbox.h_range.end;
        var hstart = frame.bbox.h_range.start;
        var vend = frame.bbox.v_range.end;
        var vstart = frame.bbox.v_range.start;
        // current aspect of cursor-defined box
        var vw = Math.abs(base_point[0] - curpoint[0]);
        var vh = Math.abs(base_point[1] - curpoint[1]);
        var va = vh == 0 ? 0 : vw / vh;
        var xmod = (va >= a ? [1, va / a] : [a / va, 1])[0];
        // OK the code blocks below merit some explanation. They do:
        //
        // compute left/right, pin to frame if necessary
        // compute top/bottom (based on new left/right), pin to frame if necessary
        // recompute left/right (based on top/bottom), in case top/bottom were pinned
        // base_point[0] is left
        var left;
        var right;
        if (base_point[0] <= curpoint[0]) {
            left = base_point[0];
            right = base_point[0] + vw * xmod;
            if (right > hend)
                right = hend;
            // base_point[0] is right
        }
        else {
            right = base_point[0];
            left = base_point[0] - vw * xmod;
            if (left < hstart)
                left = hstart;
        }
        vw = Math.abs(right - left);
        // base_point[1] is bottom
        var top;
        var bottom;
        if (base_point[1] <= curpoint[1]) {
            bottom = base_point[1];
            top = base_point[1] + vw / a;
            if (top > vend)
                top = vend;
            // base_point[1] is top
        }
        else {
            top = base_point[1];
            bottom = base_point[1] - vw / a;
            if (bottom < vstart)
                bottom = vstart;
        }
        vh = Math.abs(top - bottom);
        // base_point[0] is left
        if (base_point[0] <= curpoint[0])
            right = base_point[0] + a * vh;
        // base_point[0] is right
        else
            left = base_point[0] - a * vh;
        return [[left, right], [bottom, top]];
    };
    BoxZoomToolView.prototype._compute_limits = function (curpoint) {
        var _a, _b;
        var frame = this.plot_model.frame;
        var dims = this.model.dimensions;
        var base_point = this._base_point;
        if (this.model.origin == "center") {
            var cx = base_point[0], cy = base_point[1];
            var dx = curpoint[0], dy = curpoint[1];
            base_point = [cx - (dx - cx), cy - (dy - cy)];
        }
        var sx;
        var sy;
        if (this.model.match_aspect && dims == 'both')
            _a = this._match_aspect(base_point, curpoint, frame), sx = _a[0], sy = _a[1];
        else
            _b = this.model._get_dim_limits(base_point, curpoint, frame, dims), sx = _b[0], sy = _b[1];
        return [sx, sy];
    };
    BoxZoomToolView.prototype._pan_start = function (ev) {
        this._base_point = [ev.sx, ev.sy];
    };
    BoxZoomToolView.prototype._pan = function (ev) {
        var curpoint = [ev.sx, ev.sy];
        var _a = this._compute_limits(curpoint), sx = _a[0], sy = _a[1];
        this.model.overlay.update({ left: sx[0], right: sx[1], top: sy[0], bottom: sy[1] });
    };
    BoxZoomToolView.prototype._pan_end = function (ev) {
        var curpoint = [ev.sx, ev.sy];
        var _a = this._compute_limits(curpoint), sx = _a[0], sy = _a[1];
        this._update(sx, sy);
        this.model.overlay.update({ left: null, right: null, top: null, bottom: null });
        this._base_point = null;
    };
    BoxZoomToolView.prototype._update = function (_a, _b) {
        var sx0 = _a[0], sx1 = _a[1];
        var sy0 = _b[0], sy1 = _b[1];
        // If the viewing window is too small, no-op: it is likely that the user did
        // not intend to make this box zoom and instead was trying to cancel out of the
        // zoom, a la matplotlib's ToolZoom. Like matplotlib, set the threshold at 5 pixels.
        if (Math.abs(sx1 - sx0) <= 5 || Math.abs(sy1 - sy0) <= 5)
            return;
        var _c = this.plot_model.frame, xscales = _c.xscales, yscales = _c.yscales;
        var xrs = {};
        for (var name_1 in xscales) {
            var scale = xscales[name_1];
            var _d = scale.r_invert(sx0, sx1), start = _d[0], end = _d[1];
            xrs[name_1] = { start: start, end: end };
        }
        var yrs = {};
        for (var name_2 in yscales) {
            var scale = yscales[name_2];
            var _e = scale.r_invert(sy0, sy1), start = _e[0], end = _e[1];
            yrs[name_2] = { start: start, end: end };
        }
        var zoom_info = {
            xrs: xrs,
            yrs: yrs,
        };
        this.plot_view.push_state('box_zoom', { range: zoom_info });
        this.plot_view.update_range(zoom_info);
    };
    return BoxZoomToolView;
}(gesture_tool_1.GestureToolView));
exports.BoxZoomToolView = BoxZoomToolView;
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
var BoxZoomTool = /** @class */ (function (_super) {
    tslib_1.__extends(BoxZoomTool, _super);
    function BoxZoomTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Box Zoom";
        _this.icon = "bk-tool-icon-box-zoom";
        _this.event_type = "pan";
        _this.default_order = 20;
        return _this;
    }
    BoxZoomTool.initClass = function () {
        this.prototype.type = "BoxZoomTool";
        this.prototype.default_view = BoxZoomToolView;
        this.define({
            dimensions: [p.Dimensions, "both"],
            overlay: [p.Instance, DEFAULT_BOX_OVERLAY],
            match_aspect: [p.Bool, false],
            origin: [p.String, "corner"],
        });
    };
    Object.defineProperty(BoxZoomTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    return BoxZoomTool;
}(gesture_tool_1.GestureTool));
exports.BoxZoomTool = BoxZoomTool;
BoxZoomTool.initClass();
