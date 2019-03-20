"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var view_1 = require("core/view");
var array_1 = require("core/util/array");
var model_1 = require("../../model");
var ToolView = /** @class */ (function (_super) {
    tslib_1.__extends(ToolView, _super);
    function ToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ToolView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.plot_view = options.plot_view;
    };
    Object.defineProperty(ToolView.prototype, "plot_model", {
        get: function () {
            return this.plot_view.model;
        },
        enumerable: true,
        configurable: true
    });
    ToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.active.change, function () {
            if (_this.model.active)
                _this.activate();
            else
                _this.deactivate();
        });
    };
    // activate is triggered by toolbar ui actions
    ToolView.prototype.activate = function () { };
    // deactivate is triggered by toolbar ui actions
    ToolView.prototype.deactivate = function () { };
    return ToolView;
}(view_1.View));
exports.ToolView = ToolView;
var Tool = /** @class */ (function (_super) {
    tslib_1.__extends(Tool, _super);
    function Tool(attrs) {
        return _super.call(this, attrs) || this;
    }
    Tool.initClass = function () {
        this.prototype.type = "Tool";
        this.internal({
            active: [p.Boolean, false],
        });
    };
    Object.defineProperty(Tool.prototype, "synthetic_renderers", {
        get: function () {
            return [];
        },
        enumerable: true,
        configurable: true
    });
    // utility function to return a tool name, modified
    // by the active dimenions. Used by tools that have dimensions
    Tool.prototype._get_dim_tooltip = function (name, dims) {
        switch (dims) {
            case "width": return name + " (x-axis)";
            case "height": return name + " (y-axis)";
            case "both": return name;
        }
    };
    // utility function to get limits along both dimensions, given
    // optional dimensional constraints
    Tool.prototype._get_dim_limits = function (_a, _b, frame, dims) {
        var sx0 = _a[0], sy0 = _a[1];
        var sx1 = _b[0], sy1 = _b[1];
        var hr = frame.bbox.h_range;
        var sxlim;
        if (dims == 'width' || dims == 'both') {
            sxlim = [array_1.min([sx0, sx1]), array_1.max([sx0, sx1])];
            sxlim = [array_1.max([sxlim[0], hr.start]), array_1.min([sxlim[1], hr.end])];
        }
        else
            sxlim = [hr.start, hr.end];
        var vr = frame.bbox.v_range;
        var sylim;
        if (dims == 'height' || dims == 'both') {
            sylim = [array_1.min([sy0, sy1]), array_1.max([sy0, sy1])];
            sylim = [array_1.max([sylim[0], vr.start]), array_1.min([sylim[1], vr.end])];
        }
        else
            sylim = [vr.start, vr.end];
        return [sxlim, sylim];
    };
    return Tool;
}(model_1.Model));
exports.Tool = Tool;
Tool.initClass();
