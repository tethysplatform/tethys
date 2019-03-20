"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var logging_1 = require("core/logging");
var p = require("core/properties");
var dom_1 = require("core/dom");
var input_widget_1 = require("./input_widget");
var TextInputView = /** @class */ (function (_super) {
    tslib_1.__extends(TextInputView, _super);
    function TextInputView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TextInputView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    TextInputView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    TextInputView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-widget-form-group");
    };
    TextInputView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var labelEl = dom_1.label({ for: this.model.id }, this.model.title);
        this.el.appendChild(labelEl);
        this.inputEl = dom_1.input({
            type: "text",
            class: "bk-widget-form-input",
            id: this.model.id,
            name: this.model.name,
            value: this.model.value,
            disabled: this.model.disabled,
            placeholder: this.model.placeholder,
        });
        this.inputEl.addEventListener("change", function () { return _this.change_input(); });
        this.el.appendChild(this.inputEl);
        // TODO - This 35 is a hack we should be able to compute it
        if (this.model.height)
            this.inputEl.style.height = this.model.height - 35 + "px";
    };
    TextInputView.prototype.change_input = function () {
        var value = this.inputEl.value;
        logging_1.logger.debug("widget/text_input: value = " + value);
        this.model.value = value;
        _super.prototype.change_input.call(this);
    };
    return TextInputView;
}(input_widget_1.InputWidgetView));
exports.TextInputView = TextInputView;
var TextInput = /** @class */ (function (_super) {
    tslib_1.__extends(TextInput, _super);
    function TextInput(attrs) {
        return _super.call(this, attrs) || this;
    }
    TextInput.initClass = function () {
        this.prototype.type = "TextInput";
        this.prototype.default_view = TextInputView;
        this.define({
            value: [p.String, ""],
            placeholder: [p.String, ""],
        });
    };
    return TextInput;
}(input_widget_1.InputWidget));
exports.TextInput = TextInput;
TextInput.initClass();
