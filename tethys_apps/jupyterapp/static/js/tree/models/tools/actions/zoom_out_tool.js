"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var zoom_1 = require("core/util/zoom");
var p = require("core/properties");
var ZoomOutToolView = /** @class */ (function (_super) {
    tslib_1.__extends(ZoomOutToolView, _super);
    function ZoomOutToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ZoomOutToolView.prototype.doit = function () {
        var frame = this.plot_model.frame;
        var dims = this.model.dimensions;
        // restrict to axis configured in tool's dimensions property
        var h_axis = dims == 'width' || dims == 'both';
        var v_axis = dims == 'height' || dims == 'both';
        // zooming out requires a negative factor to scale_range
        var zoom_info = zoom_1.scale_range(frame, -this.model.factor, h_axis, v_axis);
        this.plot_view.push_state('zoom_out', { range: zoom_info });
        this.plot_view.update_range(zoom_info, false, true);
        if (this.model.document)
            this.model.document.interactive_start(this.plot_model.plot);
    };
    return ZoomOutToolView;
}(action_tool_1.ActionToolView));
exports.ZoomOutToolView = ZoomOutToolView;
var ZoomOutTool = /** @class */ (function (_super) {
    tslib_1.__extends(ZoomOutTool, _super);
    function ZoomOutTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Zoom Out";
        _this.icon = "bk-tool-icon-zoom-out";
        return _this;
    }
    ZoomOutTool.initClass = function () {
        this.prototype.type = "ZoomOutTool";
        this.prototype.default_view = ZoomOutToolView;
        this.define({
            factor: [p.Percent, 0.1],
            dimensions: [p.Dimensions, "both"],
        });
    };
    Object.defineProperty(ZoomOutTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    return ZoomOutTool;
}(action_tool_1.ActionTool));
exports.ZoomOutTool = ZoomOutTool;
ZoomOutTool.initClass();
