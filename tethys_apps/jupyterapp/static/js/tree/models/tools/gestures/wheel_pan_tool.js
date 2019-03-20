"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gesture_tool_1 = require("./gesture_tool");
var p = require("core/properties");
var WheelPanToolView = /** @class */ (function (_super) {
    tslib_1.__extends(WheelPanToolView, _super);
    function WheelPanToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WheelPanToolView.prototype._scroll = function (ev) {
        var factor = this.model.speed * ev.delta;
        // clamp the magnitude of factor, if it is > 1 bad things happen
        if (factor > 0.9)
            factor = 0.9;
        else if (factor < -0.9)
            factor = -0.9;
        this._update_ranges(factor);
    };
    WheelPanToolView.prototype._update_ranges = function (factor) {
        var frame = this.plot_model.frame;
        var hr = frame.bbox.h_range;
        var vr = frame.bbox.v_range;
        var _a = [hr.start, hr.end], sx_low = _a[0], sx_high = _a[1];
        var _b = [vr.start, vr.end], sy_low = _b[0], sy_high = _b[1];
        var sx0;
        var sx1;
        var sy0;
        var sy1;
        switch (this.model.dimension) {
            case "height": {
                var sy_range = Math.abs(sy_high - sy_low);
                sx0 = sx_low;
                sx1 = sx_high;
                sy0 = sy_low - sy_range * factor;
                sy1 = sy_high - sy_range * factor;
                break;
            }
            case "width": {
                var sx_range = Math.abs(sx_high - sx_low);
                sx0 = sx_low - sx_range * factor;
                sx1 = sx_high - sx_range * factor;
                sy0 = sy_low;
                sy1 = sy_high;
                break;
            }
            default:
                throw new Error("this shouldn't have happened");
        }
        var xscales = frame.xscales, yscales = frame.yscales;
        var xrs = {};
        for (var name_1 in xscales) {
            var scale = xscales[name_1];
            var _c = scale.r_invert(sx0, sx1), start = _c[0], end = _c[1];
            xrs[name_1] = { start: start, end: end };
        }
        var yrs = {};
        for (var name_2 in yscales) {
            var scale = yscales[name_2];
            var _d = scale.r_invert(sy0, sy1), start = _d[0], end = _d[1];
            yrs[name_2] = { start: start, end: end };
        }
        // OK this sucks we can't set factor independently in each direction. It is used
        // for GMap plots, and GMap plots always preserve aspect, so effective the value
        // of 'dimensions' is ignored.
        var pan_info = {
            xrs: xrs,
            yrs: yrs,
            factor: factor,
        };
        this.plot_view.push_state('wheel_pan', { range: pan_info });
        this.plot_view.update_range(pan_info, false, true);
        if (this.model.document != null)
            this.model.document.interactive_start(this.plot_model.plot);
    };
    return WheelPanToolView;
}(gesture_tool_1.GestureToolView));
exports.WheelPanToolView = WheelPanToolView;
var WheelPanTool = /** @class */ (function (_super) {
    tslib_1.__extends(WheelPanTool, _super);
    function WheelPanTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Wheel Pan";
        _this.icon = "bk-tool-icon-wheel-pan";
        _this.event_type = "scroll";
        _this.default_order = 12;
        return _this;
    }
    WheelPanTool.initClass = function () {
        this.prototype.type = 'WheelPanTool';
        this.prototype.default_view = WheelPanToolView;
        this.define({
            dimension: [p.Dimension, "width"],
        });
        this.internal({
            speed: [p.Number, 1 / 1000],
        });
    };
    Object.defineProperty(WheelPanTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimension);
        },
        enumerable: true,
        configurable: true
    });
    return WheelPanTool;
}(gesture_tool_1.GestureTool));
exports.WheelPanTool = WheelPanTool;
WheelPanTool.initClass();
