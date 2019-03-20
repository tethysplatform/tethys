"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var inspect_tool_1 = require("./inspect_tool");
var span_1 = require("../../annotations/span");
var p = require("core/properties");
var object_1 = require("core/util/object");
var CrosshairToolView = /** @class */ (function (_super) {
    tslib_1.__extends(CrosshairToolView, _super);
    function CrosshairToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CrosshairToolView.prototype._move = function (ev) {
        if (!this.model.active)
            return;
        var sx = ev.sx, sy = ev.sy;
        if (!this.plot_model.frame.bbox.contains(sx, sy))
            this._update_spans(null, null);
        else
            this._update_spans(sx, sy);
    };
    CrosshairToolView.prototype._move_exit = function (_e) {
        this._update_spans(null, null);
    };
    CrosshairToolView.prototype._update_spans = function (x, y) {
        var dims = this.model.dimensions;
        if (dims == "width" || dims == "both")
            this.model.spans.width.computed_location = y;
        if (dims == "height" || dims == "both")
            this.model.spans.height.computed_location = x;
    };
    return CrosshairToolView;
}(inspect_tool_1.InspectToolView));
exports.CrosshairToolView = CrosshairToolView;
var CrosshairTool = /** @class */ (function (_super) {
    tslib_1.__extends(CrosshairTool, _super);
    function CrosshairTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Crosshair";
        _this.icon = "bk-tool-icon-crosshair";
        return _this;
    }
    CrosshairTool.initClass = function () {
        this.prototype.type = "CrosshairTool";
        this.prototype.default_view = CrosshairToolView;
        this.define({
            dimensions: [p.Dimensions, "both"],
            line_color: [p.Color, 'black'],
            line_width: [p.Number, 1],
            line_alpha: [p.Number, 1.0],
        });
        this.internal({
            location_units: [p.SpatialUnits, "screen"],
            render_mode: [p.RenderMode, "css"],
            spans: [p.Any],
        });
    };
    Object.defineProperty(CrosshairTool.prototype, "tooltip", {
        get: function () {
            return this._get_dim_tooltip("Crosshair", this.dimensions);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(CrosshairTool.prototype, "synthetic_renderers", {
        get: function () {
            return object_1.values(this.spans);
        },
        enumerable: true,
        configurable: true
    });
    CrosshairTool.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.spans = {
            width: new span_1.Span({
                for_hover: true,
                dimension: "width",
                render_mode: this.render_mode,
                location_units: this.location_units,
                line_color: this.line_color,
                line_width: this.line_width,
                line_alpha: this.line_alpha,
            }),
            height: new span_1.Span({
                for_hover: true,
                dimension: "height",
                render_mode: this.render_mode,
                location_units: this.location_units,
                line_color: this.line_color,
                line_width: this.line_width,
                line_alpha: this.line_alpha,
            }),
        };
    };
    return CrosshairTool;
}(inspect_tool_1.InspectTool));
exports.CrosshairTool = CrosshairTool;
CrosshairTool.initClass();
