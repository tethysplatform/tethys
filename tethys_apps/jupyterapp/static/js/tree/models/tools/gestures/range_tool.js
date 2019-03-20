"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var box_annotation_1 = require("../../annotations/box_annotation");
var logging_1 = require("core/logging");
var p = require("core/properties");
var gesture_tool_1 = require("./gesture_tool");
// TODO (bev) This would be better directly with BoxAnnotation, but hard
// to test on a view. Move when "View Models" are implemented
function is_near(pos, value, scale, tolerance) {
    if (value == null)
        return false;
    var svalue = scale.compute(value);
    return Math.abs(pos - svalue) < tolerance;
}
exports.is_near = is_near;
// TODO (bev) This would be better directly with BoxAnnotation, but hard
// to test on a view. Move when "View Models" are implemented
function is_inside(sx, sy, xscale, yscale, overlay) {
    var result = true;
    if (overlay.left != null && overlay.right != null) {
        var x = xscale.invert(sx);
        if (x < overlay.left || x > overlay.right)
            result = false;
    }
    if (overlay.bottom != null && overlay.top != null) {
        var y = yscale.invert(sy);
        if (y < overlay.bottom || y > overlay.top)
            result = false;
    }
    return result;
}
exports.is_inside = is_inside;
function compute_value(value, scale, sdelta, range) {
    var svalue = scale.compute(value);
    var new_value = scale.invert(svalue + sdelta);
    if (new_value >= range.start && new_value <= range.end)
        return new_value;
    return value;
}
exports.compute_value = compute_value;
function update_range(range, scale, delta, plot_range) {
    var _a = scale.r_compute(range.start, range.end), sstart = _a[0], send = _a[1];
    var _b = scale.r_invert(sstart + delta, send + delta), start = _b[0], end = _b[1];
    if (start >= plot_range.start && start <= plot_range.end &&
        end >= plot_range.start && end <= plot_range.end) {
        range.start = start;
        range.end = end;
    }
}
exports.update_range = update_range;
var RangeToolView = /** @class */ (function (_super) {
    tslib_1.__extends(RangeToolView, _super);
    function RangeToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RangeToolView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.side = 0 /* None */;
        this.model.update_overlay_from_ranges();
    };
    RangeToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        if (this.model.x_range != null)
            this.connect(this.model.x_range.change, function () { return _this.model.update_overlay_from_ranges(); });
        if (this.model.y_range != null)
            this.connect(this.model.y_range.change, function () { return _this.model.update_overlay_from_ranges(); });
    };
    RangeToolView.prototype._pan_start = function (ev) {
        this.last_dx = 0;
        this.last_dy = 0;
        var xr = this.model.x_range;
        var yr = this.model.y_range;
        var frame = this.plot_model.frame;
        var xscale = frame.xscales.default;
        var yscale = frame.yscales.default;
        var overlay = this.model.overlay;
        var left = overlay.left, right = overlay.right, top = overlay.top, bottom = overlay.bottom;
        var tolerance = this.model.overlay.properties.line_width.value() + box_annotation_1.EDGE_TOLERANCE;
        if (xr != null && this.model.x_interaction) {
            if (is_near(ev.sx, left, xscale, tolerance))
                this.side = 1 /* Left */;
            else if (is_near(ev.sx, right, xscale, tolerance))
                this.side = 2 /* Right */;
            else if (is_inside(ev.sx, ev.sy, xscale, yscale, overlay)) {
                this.side = 3 /* LeftRight */;
            }
        }
        if (yr != null && this.model.y_interaction) {
            if (this.side == 0 /* None */ && is_near(ev.sy, bottom, yscale, tolerance))
                this.side = 4 /* Bottom */;
            if (this.side == 0 /* None */ && is_near(ev.sy, top, yscale, tolerance))
                this.side = 5 /* Top */;
            else if (is_inside(ev.sx, ev.sy, xscale, yscale, this.model.overlay)) {
                if (this.side == 3 /* LeftRight */)
                    this.side = 7 /* LeftRightBottomTop */;
                else
                    this.side = 6 /* BottomTop */;
            }
        }
    };
    RangeToolView.prototype._pan = function (ev) {
        var frame = this.plot_model.frame;
        var new_dx = ev.deltaX - this.last_dx;
        var new_dy = ev.deltaY - this.last_dy;
        var xr = this.model.x_range;
        var yr = this.model.y_range;
        var xscale = frame.xscales.default;
        var yscale = frame.yscales.default;
        if (xr != null) {
            if (this.side == 3 /* LeftRight */ || this.side == 7 /* LeftRightBottomTop */)
                update_range(xr, xscale, new_dx, frame.x_range);
            else if (this.side == 1 /* Left */)
                xr.start = compute_value(xr.start, xscale, new_dx, frame.x_range);
            else if (this.side == 2 /* Right */)
                xr.end = compute_value(xr.end, xscale, new_dx, frame.x_range);
        }
        if (yr != null) {
            if (this.side == 6 /* BottomTop */ || this.side == 7 /* LeftRightBottomTop */)
                update_range(yr, yscale, new_dy, frame.y_range);
            else if (this.side == 4 /* Bottom */)
                yr.start = compute_value(yr.start, yscale, new_dy, frame.y_range);
            else if (this.side == 5 /* Top */)
                yr.end = compute_value(yr.end, yscale, new_dy, frame.y_range);
        }
        this.last_dx = ev.deltaX;
        this.last_dy = ev.deltaY;
    };
    RangeToolView.prototype._pan_end = function (_ev) {
        this.side = 0 /* None */;
    };
    return RangeToolView;
}(gesture_tool_1.GestureToolView));
exports.RangeToolView = RangeToolView;
var DEFAULT_RANGE_OVERLAY = function () {
    return new box_annotation_1.BoxAnnotation({
        level: "overlay",
        render_mode: "css",
        fill_color: "lightgrey",
        fill_alpha: { value: 0.5 },
        line_color: { value: "black" },
        line_alpha: { value: 1.0 },
        line_width: { value: 0.5 },
        line_dash: [2, 2],
    });
};
var RangeTool = /** @class */ (function (_super) {
    tslib_1.__extends(RangeTool, _super);
    function RangeTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Range Tool";
        _this.icon = "bk-tool-icon-range";
        _this.event_type = "pan";
        _this.default_order = 1;
        return _this;
    }
    RangeTool.initClass = function () {
        this.prototype.type = "RangeTool";
        this.prototype.default_view = RangeToolView;
        this.define({
            x_range: [p.Instance, null],
            x_interaction: [p.Bool, true],
            y_range: [p.Instance, null],
            y_interaction: [p.Bool, true],
            overlay: [p.Instance, DEFAULT_RANGE_OVERLAY],
        });
    };
    RangeTool.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.overlay.in_cursor = "grab";
        this.overlay.ew_cursor = this.x_range != null && this.x_interaction ? "ew-resize" : null;
        this.overlay.ns_cursor = this.y_range != null && this.y_interaction ? "ns-resize" : null;
    };
    RangeTool.prototype.update_overlay_from_ranges = function () {
        if (this.x_range == null && this.y_range == null) {
            this.overlay.left = null;
            this.overlay.right = null;
            this.overlay.bottom = null;
            this.overlay.top = null;
            logging_1.logger.warn('RangeTool not configured with any Ranges.');
        }
        if (this.x_range == null) {
            this.overlay.left = null;
            this.overlay.right = null;
        }
        else {
            this.overlay.left = this.x_range.start;
            this.overlay.right = this.x_range.end;
        }
        if (this.y_range == null) {
            this.overlay.bottom = null;
            this.overlay.top = null;
        }
        else {
            this.overlay.bottom = this.y_range.start;
            this.overlay.top = this.y_range.end;
        }
    };
    return RangeTool;
}(gesture_tool_1.GestureTool));
exports.RangeTool = RangeTool;
RangeTool.initClass();
