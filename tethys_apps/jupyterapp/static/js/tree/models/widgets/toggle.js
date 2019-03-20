"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var abstract_button_1 = require("./abstract_button");
var p = require("core/properties");
var ToggleView = /** @class */ (function (_super) {
    tslib_1.__extends(ToggleView, _super);
    function ToggleView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ToggleView.prototype.render = function () {
        _super.prototype.render.call(this);
        if (this.model.active)
            this.buttonEl.classList.add("bk-bs-active");
    };
    ToggleView.prototype.change_input = function () {
        this.model.active = !this.model.active;
        _super.prototype.change_input.call(this);
    };
    return ToggleView;
}(abstract_button_1.AbstractButtonView));
exports.ToggleView = ToggleView;
var Toggle = /** @class */ (function (_super) {
    tslib_1.__extends(Toggle, _super);
    function Toggle(attrs) {
        return _super.call(this, attrs) || this;
    }
    Toggle.initClass = function () {
        this.prototype.type = "Toggle";
        this.prototype.default_view = ToggleView;
        this.define({
            active: [p.Bool, false],
        });
        this.override({
            label: "Toggle",
        });
    };
    return Toggle;
}(abstract_button_1.AbstractButton));
exports.Toggle = Toggle;
Toggle.initClass();
