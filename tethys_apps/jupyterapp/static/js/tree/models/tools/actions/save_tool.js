"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var SaveToolView = /** @class */ (function (_super) {
    tslib_1.__extends(SaveToolView, _super);
    function SaveToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SaveToolView.prototype.doit = function () {
        this.plot_view.save("bokeh_plot");
    };
    return SaveToolView;
}(action_tool_1.ActionToolView));
exports.SaveToolView = SaveToolView;
var SaveTool = /** @class */ (function (_super) {
    tslib_1.__extends(SaveTool, _super);
    function SaveTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Save";
        _this.icon = "bk-tool-icon-save";
        return _this;
    }
    SaveTool.initClass = function () {
        this.prototype.type = "SaveTool";
        this.prototype.default_view = SaveToolView;
    };
    return SaveTool;
}(action_tool_1.ActionTool));
exports.SaveTool = SaveTool;
SaveTool.initClass();
