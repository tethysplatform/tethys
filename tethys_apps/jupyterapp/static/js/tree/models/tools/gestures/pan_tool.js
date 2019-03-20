"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gesture_tool_1 = require("./gesture_tool");
var p = require("core/properties");
var PanToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PanToolView, _super);
    function PanToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PanToolView.prototype._pan_start = function (ev) {
        this.last_dx = 0;
        this.last_dy = 0;
        var sx = ev.sx, sy = ev.sy;
        var bbox = this.plot_model.frame.bbox;
        if (!bbox.contains(sx, sy)) {
            var hr = bbox.h_range;
            var vr = bbox.v_range;
            if (sx < hr.start || sx > hr.end)
                this.v_axis_only = true;
            if (sy < vr.start || sy > vr.end)
                this.h_axis_only = true;
        }
        if (this.model.document != null)
            this.model.document.interactive_start(this.plot_model.plot);
    };
    PanToolView.prototype._pan = function (ev) {
        this._update(ev.deltaX, ev.deltaY);
        if (this.model.document != null)
            this.model.document.interactive_start(this.plot_model.plot);
    };
    PanToolView.prototype._pan_end = function (_e) {
        this.h_axis_only = false;
        this.v_axis_only = false;
        if (this.pan_info != null)
            this.plot_view.push_state('pan', { range: this.pan_info });
    };
    PanToolView.prototype._update = function (dx, dy) {
        var frame = this.plot_model.frame;
        var new_dx = dx - this.last_dx;
        var new_dy = dy - this.last_dy;
        var hr = frame.bbox.h_range;
        var sx_low = hr.start - new_dx;
        var sx_high = hr.end - new_dx;
        var vr = frame.bbox.v_range;
        var sy_low = vr.start - new_dy;
        var sy_high = vr.end - new_dy;
        var dims = this.model.dimensions;
        var sx0;
        var sx1;
        var sdx;
        if ((dims == 'width' || dims == 'both') && !this.v_axis_only) {
            sx0 = sx_low;
            sx1 = sx_high;
            sdx = -new_dx;
        }
        else {
            sx0 = hr.start;
            sx1 = hr.end;
            sdx = 0;
        }
        var sy0;
        var sy1;
        var sdy;
        if ((dims == 'height' || dims == 'both') && !this.h_axis_only) {
            sy0 = sy_low;
            sy1 = sy_high;
            sdy = -new_dy;
        }
        else {
            sy0 = vr.start;
            sy1 = vr.end;
            sdy = 0;
        }
        this.last_dx = dx;
        this.last_dy = dy;
        var xscales = frame.xscales, yscales = frame.yscales;
        var xrs = {};
        for (var name_1 in xscales) {
            var scale = xscales[name_1];
            var _a = scale.r_invert(sx0, sx1), start = _a[0], end = _a[1];
            xrs[name_1] = { start: start, end: end };
        }
        var yrs = {};
        for (var name_2 in yscales) {
            var scale = yscales[name_2];
            var _b = scale.r_invert(sy0, sy1), start = _b[0], end = _b[1];
            yrs[name_2] = { start: start, end: end };
        }
        this.pan_info = {
            xrs: xrs,
            yrs: yrs,
            sdx: sdx,
            sdy: sdy,
        };
        this.plot_view.update_range(this.pan_info, true);
    };
    return PanToolView;
}(gesture_tool_1.GestureToolView));
exports.PanToolView = PanToolView;
var PanTool = /** @class */ (function (_super) {
    tslib_1.__extends(PanTool, _super);
    function PanTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Pan";
        _this.event_type = "pan";
        _this.default_order = 10;
        return _this;
    }
    PanTool.initClass = function () {
        this.prototype.type = "PanTool";
        this.prototype.default_view = PanToolView;
        this.define({
            dimensions: [p.Dimensions, "both"],
        });
    };
    Object.defineProperty(PanTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip("Pan", this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(PanTool.prototype, "icon", {
        get: function () {
            switch (this.dimensions) {
                case "both": return "bk-tool-icon-pan";
                case "width": return "bk-tool-icon-xpan";
                case "height": return "bk-tool-icon-ypan";
            }
        },
        enumerable: true,
        configurable: true
    });
    return PanTool;
}(gesture_tool_1.GestureTool));
exports.PanTool = PanTool;
PanTool.initClass();
