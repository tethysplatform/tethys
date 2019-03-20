"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var button_tool_1 = require("../button_tool");
var on_off_button_1 = require("../on_off_button");
var GestureToolView = /** @class */ (function (_super) {
    tslib_1.__extends(GestureToolView, _super);
    function GestureToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return GestureToolView;
}(button_tool_1.ButtonToolView));
exports.GestureToolView = GestureToolView;
var GestureTool = /** @class */ (function (_super) {
    tslib_1.__extends(GestureTool, _super);
    function GestureTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.button_view = on_off_button_1.OnOffButtonView;
        return _this;
    }
    GestureTool.initClass = function () {
        this.prototype.type = "GestureTool";
    };
    return GestureTool;
}(button_tool_1.ButtonTool));
exports.GestureTool = GestureTool;
GestureTool.initClass();
