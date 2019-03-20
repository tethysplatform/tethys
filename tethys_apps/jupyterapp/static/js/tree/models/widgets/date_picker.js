"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var input_widget_1 = require("./input_widget");
var dom_1 = require("core/dom");
var p = require("core/properties");
var Pikaday = require("pikaday");
Pikaday.prototype.adjustPosition = function () {
    if (this._o.container)
        return;
    this.el.style.position = 'absolute';
    var field = this._o.trigger;
    var width = this.el.offsetWidth;
    var height = this.el.offsetHeight;
    var viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    var viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    var scrollTop = window.pageYOffset || document.body.scrollTop || document.documentElement.scrollTop;
    var clientRect = field.getBoundingClientRect();
    var left = clientRect.left + window.pageXOffset;
    var top = clientRect.bottom + window.pageYOffset;
    // adjust left/top origin to bk-root
    left -= this.el.parentElement.offsetLeft;
    top -= this.el.parentElement.offsetTop;
    // default position is bottom & left
    if ((this._o.reposition && left + width > viewportWidth) ||
        (this._o.position.indexOf('right') > -1 && left - width + field.offsetWidth > 0))
        left = left - width + field.offsetWidth;
    if ((this._o.reposition && top + height > viewportHeight + scrollTop) ||
        (this._o.position.indexOf('top') > -1 && top - height - field.offsetHeight > 0))
        top = top - height - field.offsetHeight;
    this.el.style.left = left + 'px';
    this.el.style.top = top + 'px';
};
var DatePickerView = /** @class */ (function (_super) {
    tslib_1.__extends(DatePickerView, _super);
    function DatePickerView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DatePickerView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-widget-form-group");
    };
    DatePickerView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        if (this._picker != null)
            this._picker.destroy();
        dom_1.empty(this.el);
        this.labelEl = dom_1.label({}, this.model.title);
        this.el.appendChild(this.labelEl);
        this.inputEl = dom_1.input({ type: "text", class: "bk-widget-form-input", disabled: this.model.disabled });
        this.el.appendChild(this.inputEl);
        this._picker = new Pikaday({
            field: this.inputEl,
            defaultDate: new Date(this.model.value),
            setDefaultDate: true,
            minDate: this.model.min_date != null ? new Date(this.model.min_date) : undefined,
            maxDate: this.model.max_date != null ? new Date(this.model.max_date) : undefined,
            onSelect: function (date) { return _this._on_select(date); },
        });
        // move date picker's element from body to bk-root
        this._root_element.appendChild(this._picker.el);
    };
    DatePickerView.prototype._on_select = function (date) {
        // Always use toDateString()!
        // toString() breaks the websocket #4965.
        // toISOString() returns the wrong day (IE on day earlier) #7048
        // XXX: this should be handled by the serializer
        this.model.value = date.toDateString();
        this.change_input();
    };
    return DatePickerView;
}(input_widget_1.InputWidgetView));
exports.DatePickerView = DatePickerView;
var DatePicker = /** @class */ (function (_super) {
    tslib_1.__extends(DatePicker, _super);
    function DatePicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    DatePicker.initClass = function () {
        this.prototype.type = "DatePicker";
        this.prototype.default_view = DatePickerView;
        this.define({
            // TODO (bev) types
            value: [p.Any, new Date().toDateString()],
            min_date: [p.Any],
            max_date: [p.Any],
        });
    };
    return DatePicker;
}(input_widget_1.InputWidget));
exports.DatePicker = DatePicker;
DatePicker.initClass();
