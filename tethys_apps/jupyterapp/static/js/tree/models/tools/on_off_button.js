"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var button_tool_1 = require("./button_tool");
var OnOffButtonView = /** @class */ (function (_super) {
    tslib_1.__extends(OnOffButtonView, _super);
    function OnOffButtonView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    OnOffButtonView.prototype.render = function () {
        _super.prototype.render.call(this);
        if (this.model.active)
            this.el.classList.add('bk-active');
        else
            this.el.classList.remove('bk-active');
    };
    OnOffButtonView.prototype._clicked = function () {
        var active = this.model.active;
        this.model.active = !active;
    };
    return OnOffButtonView;
}(button_tool_1.ButtonToolButtonView));
exports.OnOffButtonView = OnOffButtonView;
