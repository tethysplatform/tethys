"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var array_1 = require("core/util/array");
var widget_1 = require("./widget");
var CheckboxButtonGroupView = /** @class */ (function (_super) {
    tslib_1.__extends(CheckboxButtonGroupView, _super);
    function CheckboxButtonGroupView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CheckboxButtonGroupView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    CheckboxButtonGroupView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    CheckboxButtonGroupView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var divEl = dom_1.div({ class: "bk-bs-btn-group" });
        this.el.appendChild(divEl);
        var active = this.model.active;
        var labels = this.model.labels;
        var _loop_1 = function (i) {
            var inputEl = dom_1.input({ type: "checkbox", value: "" + i, checked: i in active });
            inputEl.addEventListener("change", function () { return _this.model.change_input(i); });
            var labelEl = dom_1.label({ class: ["bk-bs-btn", "bk-bs-btn-" + this_1.model.button_type] }, inputEl, labels[i]);
            if (array_1.includes(active, i))
                labelEl.classList.add("bk-bs-active");
            divEl.appendChild(labelEl);
        };
        var this_1 = this;
        for (var i = 0; i < labels.length; i++) {
            _loop_1(i);
        }
    };
    return CheckboxButtonGroupView;
}(widget_1.WidgetView));
exports.CheckboxButtonGroupView = CheckboxButtonGroupView;
var CheckboxButtonGroup = /** @class */ (function (_super) {
    tslib_1.__extends(CheckboxButtonGroup, _super);
    function CheckboxButtonGroup(attrs) {
        return _super.call(this, attrs) || this;
    }
    CheckboxButtonGroup.prototype.change_input = function (i) {
        var active = array_1.copy(this.active);
        if (array_1.includes(active, i))
            array_1.removeBy(active, function (j) { return i == j; });
        else
            active.push(i);
        active.sort();
        this.active = active;
        if (this.callback != null)
            this.callback.execute(this);
    };
    CheckboxButtonGroup.initClass = function () {
        this.prototype.type = "CheckboxButtonGroup";
        this.prototype.default_view = CheckboxButtonGroupView;
        this.define({
            active: [p.Array, []],
            labels: [p.Array, []],
            button_type: [p.String, "default"],
            callback: [p.Instance],
        });
    };
    return CheckboxButtonGroup;
}(widget_1.Widget));
exports.CheckboxButtonGroup = CheckboxButtonGroup;
CheckboxButtonGroup.initClass();
