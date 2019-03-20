"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var UndoToolView = /** @class */ (function (_super) {
    tslib_1.__extends(UndoToolView, _super);
    function UndoToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    UndoToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.plot_view.state_changed, function () { return _this.model.disabled = !_this.plot_view.can_undo(); });
    };
    UndoToolView.prototype.doit = function () {
        this.plot_view.undo();
    };
    return UndoToolView;
}(action_tool_1.ActionToolView));
exports.UndoToolView = UndoToolView;
var UndoTool = /** @class */ (function (_super) {
    tslib_1.__extends(UndoTool, _super);
    function UndoTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Undo";
        _this.icon = "bk-tool-icon-undo";
        return _this;
    }
    UndoTool.initClass = function () {
        this.prototype.type = "UndoTool";
        this.prototype.default_view = UndoToolView;
        this.override({
            disabled: true,
        });
    };
    return UndoTool;
}(action_tool_1.ActionTool));
exports.UndoTool = UndoTool;
UndoTool.initClass();
