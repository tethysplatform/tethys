"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var string_1 = require("core/util/string");
var p = require("core/properties");
var widget_1 = require("./widget");
var RadioGroupView = /** @class */ (function (_super) {
    tslib_1.__extends(RadioGroupView, _super);
    function RadioGroupView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RadioGroupView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    RadioGroupView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    RadioGroupView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var name = string_1.uniqueId();
        var active = this.model.active;
        var labels = this.model.labels;
        for (var i = 0; i < labels.length; i++) {
            var text = labels[i];
            var inputEl = dom_1.input({ type: "radio", name: name, value: "" + i });
            inputEl.addEventListener("change", function () { return _this.change_input(); });
            if (this.model.disabled)
                inputEl.disabled = true;
            if (i == active)
                inputEl.checked = true;
            var labelEl = dom_1.label({}, inputEl, text);
            if (this.model.inline) {
                labelEl.classList.add("bk-bs-radio-inline");
                this.el.appendChild(labelEl);
            }
            else {
                var divEl = dom_1.div({ class: "bk-bs-radio" }, labelEl);
                this.el.appendChild(divEl);
            }
        }
    };
    RadioGroupView.prototype.change_input = function () {
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
    return RadioGroupView;
}(widget_1.WidgetView));
exports.RadioGroupView = RadioGroupView;
var RadioGroup = /** @class */ (function (_super) {
    tslib_1.__extends(RadioGroup, _super);
    function RadioGroup(attrs) {
        return _super.call(this, attrs) || this;
    }
    RadioGroup.initClass = function () {
        this.prototype.type = "RadioGroup";
        this.prototype.default_view = RadioGroupView;
        this.define({
            active: [p.Any, null],
            labels: [p.Array, []],
            inline: [p.Bool, false],
            callback: [p.Instance],
        });
    };
    return RadioGroup;
}(widget_1.Widget));
exports.RadioGroup = RadioGroup;
RadioGroup.initClass();
