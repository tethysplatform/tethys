"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var action_tool_1 = require("./action_tool");
var p = require("core/properties");
var HelpToolView = /** @class */ (function (_super) {
    tslib_1.__extends(HelpToolView, _super);
    function HelpToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    HelpToolView.prototype.doit = function () {
        window.open(this.model.redirect);
    };
    return HelpToolView;
}(action_tool_1.ActionToolView));
exports.HelpToolView = HelpToolView;
var HelpTool = /** @class */ (function (_super) {
    tslib_1.__extends(HelpTool, _super);
    function HelpTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Help";
        _this.icon = "bk-tool-icon-help";
        return _this;
    }
    HelpTool.initClass = function () {
        this.prototype.type = "HelpTool";
        this.prototype.default_view = HelpToolView;
        this.define({
            help_tooltip: [p.String, 'Click the question mark to learn more about Bokeh plot tools.'],
            redirect: [p.String, 'https://bokeh.pydata.org/en/latest/docs/user_guide/tools.html#built-in-tools'],
        });
    };
    Object.defineProperty(HelpTool.prototype, "tooltip", {
        get: function () {
            return this.help_tooltip;
        },
        enumerable: true,
        configurable: true
    });
    return HelpTool;
}(action_tool_1.ActionTool));
exports.HelpTool = HelpTool;
HelpTool.initClass();
