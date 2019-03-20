"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var array_1 = require("core/util/array");
var widget_1 = require("./widget");
var CheckboxGroupView = /** @class */ (function (_super) {
    tslib_1.__extends(CheckboxGroupView, _super);
    function CheckboxGroupView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CheckboxGroupView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    CheckboxGroupView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    CheckboxGroupView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var active = this.model.active;
        var labels = this.model.labels;
        for (var i = 0; i < labels.length; i++) {
            var text = labels[i];
            var inputEl = dom_1.input({ type: "checkbox", value: "" + i });
            inputEl.addEventListener("change", function () { return _this.change_input(); });
            if (this.model.disabled)
                inputEl.disabled = true;
            if (array_1.includes(active, i))
                inputEl.checked = true;
            var labelEl = dom_1.label({}, inputEl, text);
            if (this.model.inline) {
                labelEl.classList.add("bk-bs-checkbox-inline");
                this.el.appendChild(labelEl);
            }
            else {
                var divEl = dom_1.div({ class: "bk-bs-checkbox" }, labelEl);
                this.el.appendChild(divEl);
            }
        }
    };
    CheckboxGroupView.prototype.change_input = function () {
        var checkboxes = this.el.querySelectorAll("input");
        var active = [];
        for (var i = 0; i < checkboxes.length; i++) {
            var checkbox = checkboxes[i];
            if (checkbox.checked)
                active.push(i);
        }
        this.model.active = active;
        if (this.model.callback != null)
            this.model.callback.execute(this.model);
    };
    return CheckboxGroupView;
}(widget_1.WidgetView));
exports.CheckboxGroupView = CheckboxGroupView;
var CheckboxGroup = /** @class */ (function (_super) {
    tslib_1.__extends(CheckboxGroup, _super);
    function CheckboxGroup(attrs) {
        return _super.call(this, attrs) || this;
    }
    CheckboxGroup.initClass = function () {
        this.prototype.type = "CheckboxGroup";
        this.prototype.default_view = CheckboxGroupView;
        this.define({
            active: [p.Array, []],
            labels: [p.Array, []],
            inline: [p.Bool, false],
            callback: [p.Instance],
        });
    };
    return CheckboxGroup;
}(widget_1.Widget));
exports.CheckboxGroup = CheckboxGroup;
CheckboxGroup.initClass();
