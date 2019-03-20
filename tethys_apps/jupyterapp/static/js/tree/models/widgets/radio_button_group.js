"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var string_1 = require("core/util/string");
var p = require("core/properties");
var widget_1 = require("./widget");
var RadioButtonGroupView = /** @class */ (function (_super) {
    tslib_1.__extends(RadioButtonGroupView, _super);
    function RadioButtonGroupView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RadioButtonGroupView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    RadioButtonGroupView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    RadioButtonGroupView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var divEl = dom_1.div({ class: "bk-bs-btn-group" });
        this.el.appendChild(divEl);
        var name = string_1.uniqueId();
        var active = this.model.active;
        var labels = this.model.labels;
        for (var i = 0; i < labels.length; i++) {
            var text = labels[i];
            var inputEl = dom_1.input({ type: "radio", name: name, value: "" + i, checked: i == active });
            inputEl.addEventListener("change", function () { return _this.change_input(); });
            var labelEl = dom_1.label({ class: ["bk-bs-btn", "bk-bs-btn-" + this.model.button_type] }, inputEl, text);
            if (i == active)
                labelEl.classList.add("bk-bs-active");
            divEl.appendChild(labelEl);
        }
    };
    RadioButtonGroupView.prototype.change_input = function () {
        var radios = this.el.querySelectorAll("input");
        var active = [];
        for (var i = 0; i < radios.length; i++) {
            var radio = radios[i];
            if (radio.checked)
                active.push(i);
        }
        this.model.active = active[0];
        if (this.model.callback != null)
            this.model.callback.execute(this.model);
    };
    return RadioButtonGroupView;
}(widget_1.WidgetView));
exports.RadioButtonGroupView = RadioButtonGroupView;
var RadioButtonGroup = /** @class */ (function (_super) {
    tslib_1.__extends(RadioButtonGroup, _super);
    function RadioButtonGroup(attrs) {
        return _super.call(this, attrs) || this;
    }
    RadioButtonGroup.initClass = function () {
        this.prototype.type = "RadioButtonGroup";
        this.prototype.default_view = RadioButtonGroupView;
        this.define({
            active: [p.Any, null],
            labels: [p.Array, []],
            button_type: [p.String, "default"],
            callback: [p.Instance],
        });
    };
    return RadioButtonGroup;
}(widget_1.Widget));
exports.RadioButtonGroup = RadioButtonGroup;
RadioButtonGroup.initClass();
