"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var text_input_1 = require("./text_input");
var PasswordInputView = /** @class */ (function (_super) {
    tslib_1.__extends(PasswordInputView, _super);
    function PasswordInputView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PasswordInputView.prototype.render = function () {
        _super.prototype.render.call(this);
        this.inputEl.type = "password";
    };
    return PasswordInputView;
}(text_input_1.TextInputView));
exports.PasswordInputView = PasswordInputView;
var PasswordInput = /** @class */ (function (_super) {
    tslib_1.__extends(PasswordInput, _super);
    function PasswordInput(attrs) {
        return _super.call(this, attrs) || this;
    }
    PasswordInput.initClass = function () {
        this.prototype.type = "PasswordInput";
        this.prototype.default_view = PasswordInputView;
    };
    return PasswordInput;
}(text_input_1.TextInput));
exports.PasswordInput = PasswordInput;
PasswordInput.initClass();
