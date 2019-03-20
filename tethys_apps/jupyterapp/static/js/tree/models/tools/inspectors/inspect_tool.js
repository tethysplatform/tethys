"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var button_tool_1 = require("../button_tool");
var on_off_button_1 = require("../on_off_button");
var p = require("core/properties");
var InspectToolView = /** @class */ (function (_super) {
    tslib_1.__extends(InspectToolView, _super);
    function InspectToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return InspectToolView;
}(button_tool_1.ButtonToolView));
exports.InspectToolView = InspectToolView;
var InspectTool = /** @class */ (function (_super) {
    tslib_1.__extends(InspectTool, _super);
    function InspectTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.event_type = "move";
        return _this;
    }
    InspectTool.initClass = function () {
        this.prototype.type = "InspectTool";
        this.prototype.button_view = on_off_button_1.OnOffButtonView;
        this.define({
            toggleable: [p.Bool, true],
        });
        this.override({
            active: true,
        });
    };
    return InspectTool;
}(button_tool_1.ButtonTool));
exports.InspectTool = InspectTool;
InspectTool.initClass();
