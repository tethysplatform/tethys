"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var types_1 = require("core/util/types");
var data_structures_1 = require("core/util/data_structures");
var p = require("core/properties");
var input_widget_1 = require("./input_widget");
var MultiSelectView = /** @class */ (function (_super) {
    tslib_1.__extends(MultiSelectView, _super);
    function MultiSelectView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MultiSelectView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    MultiSelectView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.value.change, function () { return _this.render_selection(); });
        this.connect(this.model.properties.options.change, function () { return _this.render(); });
        this.connect(this.model.properties.name.change, function () { return _this.render(); });
        this.connect(this.model.properties.title.change, function () { return _this.render(); });
        this.connect(this.model.properties.size.change, function () { return _this.render(); });
        this.connect(this.model.properties.disabled.change, function () { return _this.render(); });
    };
    MultiSelectView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var labelEl = dom_1.label({ for: this.model.id }, this.model.title);
        this.el.appendChild(labelEl);
        var options = this.model.options.map(function (opt) {
            var value, _label;
            if (types_1.isString(opt))
                value = _label = opt;
            else
                value = opt[0], _label = opt[1];
            return dom_1.option({ value: value }, _label);
        });
        this.selectEl = dom_1.select({
            multiple: true,
            class: "bk-widget-form-input",
            id: this.model.id,
            name: this.model.name,
            disabled: this.model.disabled,
        }, options);
        this.selectEl.addEventListener("change", function () { return _this.change_input(); });
        this.el.appendChild(this.selectEl);
        this.render_selection();
    };
    MultiSelectView.prototype.render_selection = function () {
        var selected = new data_structures_1.Set(this.model.value);
        for (var _i = 0, _a = Array.from(this.el.querySelectorAll('option')); _i < _a.length; _i++) {
            var el = _a[_i];
            el.selected = selected.has(el.value);
        }
        // Note that some browser implementations might not reduce
        // the number of visible options for size <= 3.
        this.selectEl.size = this.model.size;
    };
    MultiSelectView.prototype.change_input = function () {
        var is_focused = this.el.querySelector('select:focus') != null;
        var values = [];
        for (var _i = 0, _a = Array.from(this.el.querySelectorAll('option')); _i < _a.length; _i++) {
            var el = _a[_i];
            if (el.selected)
                values.push(el.value);
        }
        this.model.value = values;
        _super.prototype.change_input.call(this);
        // Restore focus back to the <select> afterwards,
        // so that even if python on_change callback is invoked,
        // focus remains on <select> and one can seamlessly scroll
        // up/down.
        if (is_focused)
            this.selectEl.focus();
    };
    return MultiSelectView;
}(input_widget_1.InputWidgetView));
exports.MultiSelectView = MultiSelectView;
var MultiSelect = /** @class */ (function (_super) {
    tslib_1.__extends(MultiSelect, _super);
    function MultiSelect(attrs) {
        return _super.call(this, attrs) || this;
    }
    MultiSelect.initClass = function () {
        this.prototype.type = "MultiSelect";
        this.prototype.default_view = MultiSelectView;
        this.define({
            value: [p.Array, []],
            options: [p.Array, []],
            size: [p.Number, 4],
        });
    };
    return MultiSelect;
}(input_widget_1.InputWidget));
exports.MultiSelect = MultiSelect;
MultiSelect.initClass();
