"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var dom_1 = require("core/dom");
var build_views_1 = require("core/build_views");
var widget_1 = require("./widget");
var AbstractButtonView = /** @class */ (function (_super) {
    tslib_1.__extends(AbstractButtonView, _super);
    function AbstractButtonView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AbstractButtonView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.icon_views = {};
        this.render();
    };
    AbstractButtonView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    AbstractButtonView.prototype.remove = function () {
        build_views_1.remove_views(this.icon_views);
        _super.prototype.remove.call(this);
    };
    AbstractButtonView.prototype._render_button = function () {
        var children = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            children[_i] = arguments[_i];
        }
        return dom_1.button.apply(void 0, [{
                type: "button",
                disabled: this.model.disabled,
                class: ["bk-bs-btn", "bk-bs-btn-" + this.model.button_type],
            }].concat(children));
    };
    AbstractButtonView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        this.buttonEl = this._render_button(this.model.label);
        this.buttonEl.addEventListener("click", function (event) { return _this._button_click(event); });
        this.el.appendChild(this.buttonEl);
        var icon = this.model.icon;
        if (icon != null) {
            build_views_1.build_views(this.icon_views, [icon], { parent: this });
            dom_1.prepend(this.buttonEl, this.icon_views[icon.id].el, dom_1.nbsp);
        }
    };
    AbstractButtonView.prototype._button_click = function (event) {
        event.preventDefault();
        this.change_input();
    };
    AbstractButtonView.prototype.change_input = function () {
        if (this.model.callback != null)
            this.model.callback.execute(this.model);
    };
    return AbstractButtonView;
}(widget_1.WidgetView));
exports.AbstractButtonView = AbstractButtonView;
var AbstractButton = /** @class */ (function (_super) {
    tslib_1.__extends(AbstractButton, _super);
    function AbstractButton(attrs) {
        return _super.call(this, attrs) || this;
    }
    AbstractButton.initClass = function () {
        this.prototype.type = "AbstractButton";
        this.define({
            label: [p.String, "Button"],
            icon: [p.Instance],
            button_type: [p.String, "default"],
            callback: [p.Instance],
        });
    };
    return AbstractButton;
}(widget_1.Widget));
exports.AbstractButton = AbstractButton;
AbstractButton.initClass();
