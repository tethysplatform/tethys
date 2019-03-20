"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var zoom_1 = require("core/util/zoom");
var p = require("core/properties");
var ZoomInToolView = /** @class */ (function (_super) {
    tslib_1.__extends(ZoomInToolView, _super);
    function ZoomInToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ZoomInToolView.prototype.doit = function () {
        var frame = this.plot_model.frame;
        var dims = this.model.dimensions;
        // restrict to axis configured in tool's dimensions property
        var h_axis = dims == 'width' || dims == 'both';
        var v_axis = dims == 'height' || dims == 'both';
        var zoom_info = zoom_1.scale_range(frame, this.model.factor, h_axis, v_axis);
        this.plot_view.push_state('zoom_out', { range: zoom_info });
        this.plot_view.update_range(zoom_info, false, true);
        if (this.model.document)
            this.model.document.interactive_start(this.plot_model.plot);
    };
    return ZoomInToolView;
}(action_tool_1.ActionToolView));
exports.ZoomInToolView = ZoomInToolView;
var ZoomInTool = /** @class */ (function (_super) {
    tslib_1.__extends(ZoomInTool, _super);
    function ZoomInTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Zoom In";
        _this.icon = "bk-tool-icon-zoom-in";
        return _this;
    }
    ZoomInTool.initClass = function () {
        this.prototype.type = "ZoomInTool";
        this.prototype.default_view = ZoomInToolView;
        this.define({
            factor: [p.Percent, 0.1],
            dimensions: [p.Dimensions, "both"],
        });
    };
    Object.defineProperty(ZoomInTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    return ZoomInTool;
}(action_tool_1.ActionTool));
exports.ZoomInTool = ZoomInTool;
ZoomInTool.initClass();
