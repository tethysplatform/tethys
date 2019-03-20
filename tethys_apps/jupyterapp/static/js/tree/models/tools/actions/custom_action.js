"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var p = require("core/properties");
var types_1 = require("core/util/types");
var CustomActionButtonView = /** @class */ (function (_super) {
    tslib_1.__extends(CustomActionButtonView, _super);
    function CustomActionButtonView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CustomActionButtonView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-toolbar-button-custom-action");
    };
    return CustomActionButtonView;
}(action_tool_1.ActionToolButtonView));
exports.CustomActionButtonView = CustomActionButtonView;
var CustomActionView = /** @class */ (function (_super) {
    tslib_1.__extends(CustomActionView, _super);
    function CustomActionView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CustomActionView.prototype.doit = function () {
        var callback = this.model.callback;
        if (types_1.isFunction(callback))
            callback(this, {});
        else
            callback.execute(this, {});
    };
    return CustomActionView;
}(action_tool_1.ActionToolView));
exports.CustomActionView = CustomActionView;
var CustomAction = /** @class */ (function (_super) {
    tslib_1.__extends(CustomAction, _super);
    function CustomAction(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Custom Action";
        _this.button_view = CustomActionButtonView;
        return _this;
    }
    CustomAction.initClass = function () {
        this.prototype.type = "CustomAction";
        this.prototype.default_view = CustomActionView;
        this.define({
            action_tooltip: [p.String, 'Perform a Custom Action'],
            callback: [p.Any],
            icon: [p.String,],
        });
    };
    Object.defineProperty(CustomAction.prototype, "tooltip", {
        get: function () {
            return this.action_tooltip;
        },
        enumerable: true,
        configurable: true
    });
    return CustomAction;
}(action_tool_1.ActionTool));
exports.CustomAction = CustomAction;
CustomAction.initClass();
