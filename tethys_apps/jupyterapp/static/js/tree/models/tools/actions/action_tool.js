"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var button_tool_1 = require("../button_tool");
var signaling_1 = require("core/signaling");
var ActionToolButtonView = /** @class */ (function (_super) {
    tslib_1.__extends(ActionToolButtonView, _super);
    function ActionToolButtonView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ActionToolButtonView.prototype._clicked = function () {
        this.model.do.emit();
    };
    return ActionToolButtonView;
}(button_tool_1.ButtonToolButtonView));
exports.ActionToolButtonView = ActionToolButtonView;
var ActionToolView = /** @class */ (function (_super) {
    tslib_1.__extends(ActionToolView, _super);
    function ActionToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ActionToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.do, function () { return _this.doit(); });
    };
    return ActionToolView;
}(button_tool_1.ButtonToolView));
exports.ActionToolView = ActionToolView;
var ActionTool = /** @class */ (function (_super) {
    tslib_1.__extends(ActionTool, _super);
    function ActionTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.button_view = ActionToolButtonView;
        _this.do = new signaling_1.Signal0(_this, "do");
        return _this;
    }
    ActionTool.initClass = function () {
        this.prototype.type = "ActionTool";
    };
    return ActionTool;
}(button_tool_1.ButtonTool));
exports.ActionTool = ActionTool;
ActionTool.initClass();
