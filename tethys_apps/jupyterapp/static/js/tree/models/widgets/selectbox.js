"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var types_1 = require("core/util/types");
var logging_1 = require("core/logging");
var p = require("core/properties");
var input_widget_1 = require("./input_widget");
var SelectView = /** @class */ (function (_super) {
    tslib_1.__extends(SelectView, _super);
    function SelectView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SelectView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    SelectView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    SelectView.prototype.build_options = function (values) {
        var _this = this;
        return values.map(function (el) {
            var value, _label;
            if (types_1.isString(el))
                value = _label = el;
            else
                value = el[0], _label = el[1];
            var selected = _this.model.value == value;
            return dom_1.option({ selected: selected, value: value }, _label);
        });
    };
    SelectView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var labelEl = dom_1.label({ for: this.model.id }, this.model.title);
        this.el.appendChild(labelEl);
        var contents;
        if (types_1.isArray(this.model.options))
            contents = this.build_options(this.model.options);
        else {
            contents = [];
            var options = this.model.options;
            for (var key in options) {
                var value = options[key];
                contents.push(dom_1.optgroup({ label: key }, this.build_options(value)));
            }
        }
        this.selectEl = dom_1.select({
            class: "bk-widget-form-input",
            id: this.model.id,
            name: this.model.name,
            disabled: this.model.disabled
        }, contents);
        this.selectEl.addEventListener("change", function () { return _this.change_input(); });
        this.el.appendChild(this.selectEl);
    };
    SelectView.prototype.change_input = function () {
        var value = this.selectEl.value;
        logging_1.logger.debug("selectbox: value = " + value);
        this.model.value = value;
        _super.prototype.change_input.call(this);
    };
    return SelectView;
}(input_widget_1.InputWidgetView));
exports.SelectView = SelectView;
var Select = /** @class */ (function (_super) {
    tslib_1.__extends(Select, _super);
    function Select(attrs) {
        return _super.call(this, attrs) || this;
    }
    Select.initClass = function () {
        this.prototype.type = "Select";
        this.prototype.default_view = SelectView;
        this.define({
            value: [p.String, ''],
            options: [p.Any, []],
        });
    };
    return Select;
}(input_widget_1.InputWidget));
exports.Select = Select;
Select.initClass();
