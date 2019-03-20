"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gesture_tool_1 = require("./gesture_tool");
var zoom_1 = require("core/util/zoom");
var p = require("core/properties");
var ui_events_1 = require("core/ui_events");
var WheelZoomToolView = /** @class */ (function (_super) {
    tslib_1.__extends(WheelZoomToolView, _super);
    function WheelZoomToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WheelZoomToolView.prototype._pinch = function (ev) {
        // TODO (bev) this can probably be done much better
        var sx = ev.sx, sy = ev.sy, scale = ev.scale;
        var delta;
        if (scale >= 1)
            delta = (scale - 1) * 20.0;
        else
            delta = -20.0 / scale;
        this._scroll({ type: "mousewheel", sx: sx, sy: sy, delta: delta });
    };
    WheelZoomToolView.prototype._scroll = function (ev) {
        var frame = this.plot_model.frame;
        var hr = frame.bbox.h_range;
        var vr = frame.bbox.v_range;
        var sx = ev.sx, sy = ev.sy;
        var dims = this.model.dimensions;
        // restrict to axis configured in tool's dimensions property and if
        // zoom origin is inside of frame range/domain
        var h_axis = (dims == 'width' || dims == 'both') && hr.start < sx && sx < hr.end;
        var v_axis = (dims == 'height' || dims == 'both') && vr.start < sy && sy < vr.end;
        if ((!h_axis || !v_axis) && !this.model.zoom_on_axis) {
            return;
        }
        var factor = this.model.speed * ev.delta;
        var zoom_info = zoom_1.scale_range(frame, factor, h_axis, v_axis, { x: sx, y: sy });
        this.plot_view.push_state('wheel_zoom', { range: zoom_info });
        this.plot_view.update_range(zoom_info, false, true, this.model.maintain_focus);
        if (this.model.document != null)
            this.model.document.interactive_start(this.plot_model.plot);
    };
    return WheelZoomToolView;
}(gesture_tool_1.GestureToolView));
exports.WheelZoomToolView = WheelZoomToolView;
var WheelZoomTool = /** @class */ (function (_super) {
    tslib_1.__extends(WheelZoomTool, _super);
    function WheelZoomTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Wheel Zoom";
        _this.icon = "bk-tool-icon-wheel-zoom";
        _this.event_type = ui_events_1.is_mobile ? "pinch" : "scroll";
        _this.default_order = 10;
        return _this;
    }
    WheelZoomTool.initClass = function () {
        this.prototype.type = "WheelZoomTool";
        this.prototype.default_view = WheelZoomToolView;
        this.define({
            dimensions: [p.Dimensions, "both"],
            maintain_focus: [p.Boolean, true],
            zoom_on_axis: [p.Boolean, true],
            speed: [p.Number, 1 / 600],
        });
    };
    Object.defineProperty(WheelZoomTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    return WheelZoomTool;
}(gesture_tool_1.GestureTool));
exports.WheelZoomTool = WheelZoomTool;
WheelZoomTool.initClass();
