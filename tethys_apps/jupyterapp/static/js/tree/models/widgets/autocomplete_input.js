"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var text_input_1 = require("./text_input");
var dom_1 = require("core/dom");
var menus_1 = require("core/menus");
var p = require("core/properties");
var AutocompleteInputView = /** @class */ (function (_super) {
    tslib_1.__extends(AutocompleteInputView, _super);
    function AutocompleteInputView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AutocompleteInputView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        menus_1.clear_menus.connect(function () { return _this._clear_menu(); });
    };
    AutocompleteInputView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        this.inputEl.classList.add("bk-autocomplete-input");
        this.inputEl.addEventListener("keydown", function (event) { return _this._keydown(event); });
        this.inputEl.addEventListener("keyup", function (event) { return _this._keyup(event); });
        this.menuEl = dom_1.ul({ class: "bk-bs-dropdown-menu" });
        this.menuEl.addEventListener("click", function (event) { return _this._item_click(event); });
        this.el.appendChild(this.menuEl);
    };
    AutocompleteInputView.prototype._render_items = function (completions) {
        dom_1.empty(this.menuEl);
        for (var _i = 0, completions_1 = completions; _i < completions_1.length; _i++) {
            var text = completions_1[_i];
            var itemEl = dom_1.li({}, dom_1.a({ data: { text: text } }, text));
            this.menuEl.appendChild(itemEl);
        }
    };
    AutocompleteInputView.prototype._open_menu = function () {
        this.el.classList.add("bk-bs-open");
    };
    AutocompleteInputView.prototype._clear_menu = function () {
        this.el.classList.remove("bk-bs-open");
    };
    AutocompleteInputView.prototype._item_click = function (event) {
        event.preventDefault();
        if (event.target != event.currentTarget) {
            var el = event.target;
            var text = el.dataset.text;
            this.model.value = text;
            //this.inputEl.value = text
        }
    };
    AutocompleteInputView.prototype._keydown = function (_event) { };
    AutocompleteInputView.prototype._keyup = function (event) {
        switch (event.keyCode) {
            case dom_1.Keys.Enter: {
                console.log("enter");
                break;
            }
            case dom_1.Keys.Esc: {
                this._clear_menu();
                break;
            }
            case dom_1.Keys.Up:
            case dom_1.Keys.Down: {
                console.log("up/down");
                break;
            }
            default: {
                var value = this.inputEl.value;
                if (value.length <= 1) {
                    this._clear_menu();
                    return;
                }
                var completions = [];
                for (var _i = 0, _a = this.model.completions; _i < _a.length; _i++) {
                    var text = _a[_i];
                    if (text.indexOf(value) != -1)
                        completions.push(text);
                }
                if (completions.length == 0)
                    this._clear_menu();
                else {
                    this._render_items(completions);
                    this._open_menu();
                }
            }
        }
    };
    return AutocompleteInputView;
}(text_input_1.TextInputView));
exports.AutocompleteInputView = AutocompleteInputView;
var AutocompleteInput = /** @class */ (function (_super) {
    tslib_1.__extends(AutocompleteInput, _super);
    function AutocompleteInput(attrs) {
        return _super.call(this, attrs) || this;
    }
    AutocompleteInput.initClass = function () {
        this.prototype.type = "AutocompleteInput";
        this.prototype.default_view = AutocompleteInputView;
        this.define({
            completions: [p.Array, []],
        });
        this.internal({
            active: [p.Boolean, true],
        });
    };
    return AutocompleteInput;
}(text_input_1.TextInput));
exports.AutocompleteInput = AutocompleteInput;
AutocompleteInput.initClass();
