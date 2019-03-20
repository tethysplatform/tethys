"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var menus_1 = require("core/menus");
var p = require("core/properties");
var abstract_button_1 = require("./abstract_button");
var DropdownView = /** @class */ (function (_super) {
    tslib_1.__extends(DropdownView, _super);
    function DropdownView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DropdownView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        menus_1.clear_menus.connect(function () { return _this._clear_menu(); });
    };
    DropdownView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        if (!this.model.is_split_button) {
            this.el.classList.add("bk-bs-dropdown");
            this.buttonEl.classList.add("bk-bs-dropdown-toggle");
            this.buttonEl.appendChild(dom_1.span({ class: "bk-bs-caret" }));
        }
        else {
            this.el.classList.add("bk-bs-btn-group");
            var caretEl = this._render_button(dom_1.span({ class: "bk-bs-caret" }));
            caretEl.classList.add("bk-bs-dropdown-toggle");
            caretEl.addEventListener("click", function (event) { return _this._caret_click(event); });
            this.el.appendChild(caretEl);
        }
        if (this.model.active)
            this.el.classList.add("bk-bs-open");
        var items = [];
        for (var _i = 0, _a = this.model.menu; _i < _a.length; _i++) {
            var item = _a[_i];
            var itemEl = void 0;
            if (item != null) {
                var label = item[0], value = item[1];
                var link = dom_1.a({}, label);
                link.dataset.value = value;
                link.addEventListener("click", function (event) { return _this._item_click(event); });
                itemEl = dom_1.li({}, link);
            }
            else
                itemEl = dom_1.li({ class: "bk-bs-divider" });
            items.push(itemEl);
        }
        var menuEl = dom_1.ul({ class: "bk-bs-dropdown-menu" }, items);
        this.el.appendChild(menuEl);
    };
    DropdownView.prototype._clear_menu = function () {
        this.model.active = false;
    };
    DropdownView.prototype._toggle_menu = function () {
        var active = this.model.active;
        menus_1.clear_menus.emit();
        if (!active)
            this.model.active = true;
    };
    DropdownView.prototype._button_click = function (event) {
        event.preventDefault();
        event.stopPropagation();
        if (!this.model.is_split_button)
            this._toggle_menu();
        else {
            this._clear_menu();
            this.set_value(this.model.default_value);
        }
    };
    DropdownView.prototype._caret_click = function (event) {
        event.preventDefault();
        event.stopPropagation();
        this._toggle_menu();
    };
    DropdownView.prototype._item_click = function (event) {
        event.preventDefault();
        this._clear_menu();
        this.set_value(event.currentTarget.dataset.value);
    };
    DropdownView.prototype.set_value = function (value) {
        this.buttonEl.value = this.model.value = value;
        this.change_input();
    };
    return DropdownView;
}(abstract_button_1.AbstractButtonView));
exports.DropdownView = DropdownView;
var Dropdown = /** @class */ (function (_super) {
    tslib_1.__extends(Dropdown, _super);
    function Dropdown(attrs) {
        return _super.call(this, attrs) || this;
    }
    Dropdown.initClass = function () {
        this.prototype.type = "Dropdown";
        this.prototype.default_view = DropdownView;
        this.define({
            value: [p.String],
            default_value: [p.String],
            menu: [p.Array, []],
        });
        this.override({
            label: "Dropdown",
        });
        this.internal({
            active: [p.Boolean, false],
        });
    };
    Object.defineProperty(Dropdown.prototype, "is_split_button", {
        get: function () {
            return this.default_value != null;
        },
        enumerable: true,
        configurable: true
    });
    return Dropdown;
}(abstract_button_1.AbstractButton));
exports.Dropdown = Dropdown;
Dropdown.initClass();
