"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var ResetToolView = /** @class */ (function (_super) {
    tslib_1.__extends(ResetToolView, _super);
    function ResetToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ResetToolView.prototype.doit = function () {
        this.plot_view.reset();
    };
    return ResetToolView;
}(action_tool_1.ActionToolView));
exports.ResetToolView = ResetToolView;
var ResetTool = /** @class */ (function (_super) {
    tslib_1.__extends(ResetTool, _super);
    function ResetTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Reset";
        _this.icon = "bk-tool-icon-reset";
        return _this;
    }
    ResetTool.initClass = function () {
        this.prototype.type = "ResetTool";
        this.prototype.default_view = ResetToolView;
    };
    return ResetTool;
}(action_tool_1.ActionTool));
exports.ResetTool = ResetTool;
ResetTool.initClass();
