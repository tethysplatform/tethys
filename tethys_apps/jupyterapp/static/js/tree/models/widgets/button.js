"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var bokeh_events_1 = require("core/bokeh_events");
var abstract_button_1 = require("./abstract_button");
var ButtonView = /** @class */ (function (_super) {
    tslib_1.__extends(ButtonView, _super);
    function ButtonView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ButtonView.prototype.change_input = function () {
        this.model.trigger_event(new bokeh_events_1.ButtonClick({}));
        this.model.clicks = this.model.clicks + 1;
        _super.prototype.change_input.call(this);
    };
    return ButtonView;
}(abstract_button_1.AbstractButtonView));
exports.ButtonView = ButtonView;
var Button = /** @class */ (function (_super) {
    tslib_1.__extends(Button, _super);
    function Button(attrs) {
        return _super.call(this, attrs) || this;
    }
    Button.initClass = function () {
        this.prototype.type = "Button";
        this.prototype.default_view = ButtonView;
        this.define({
            clicks: [p.Number, 0],
        });
        bokeh_events_1.register_with_event(bokeh_events_1.ButtonClick, this);
    };
    return Button;
}(abstract_button_1.AbstractButton));
exports.Button = Button;
Button.initClass();
