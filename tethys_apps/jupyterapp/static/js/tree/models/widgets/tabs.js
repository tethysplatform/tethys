"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var array_1 = require("core/util/array");
var p = require("core/properties");
var widget_1 = require("./widget");
var TabsView = /** @class */ (function (_super) {
    tslib_1.__extends(TabsView, _super);
    function TabsView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TabsView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.tabs.change, function () { return _this.rebuild_child_views(); });
        this.connect(this.model.properties.active.change, function () { return _this.render(); });
    };
    TabsView.prototype.render = function () {
        var _this = this;
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var len = this.model.tabs.length;
        if (len == 0)
            return;
        else if (this.model.active >= len)
            this.model.active = len - 1;
        var tabs = this.model.tabs.map(function (tab, i) { return dom_1.li({}, dom_1.span({ data: { index: i } }, tab.title)); });
        tabs[this.model.active].classList.add("bk-bs-active");
        var tabsEl = dom_1.ul({ class: ["bk-bs-nav", "bk-bs-nav-tabs"] }, tabs);
        this.el.appendChild(tabsEl);
        var panels = this.model.tabs.map(function (_tab) { return dom_1.div({ class: "bk-bs-tab-pane" }); });
        panels[this.model.active].classList.add("bk-bs-active");
        var panelsEl = dom_1.div({ class: "bk-bs-tab-content" }, panels);
        this.el.appendChild(panelsEl);
        tabsEl.addEventListener("click", function (event) {
            event.preventDefault();
            if (event.target != event.currentTarget) {
                var el = event.target;
                var old_active = _this.model.active;
                var new_active = parseInt(el.dataset.index);
                if (old_active != new_active) {
                    tabs[old_active].classList.remove("bk-bs-active");
                    panels[old_active].classList.remove("bk-bs-active");
                    tabs[new_active].classList.add("bk-bs-active");
                    panels[new_active].classList.add("bk-bs-active");
                    _this.model.active = new_active;
                    if (_this.model.callback != null)
                        _this.model.callback.execute(_this.model);
                }
            }
        });
        for (var _i = 0, _a = array_1.zip(this.model.children, panels); _i < _a.length; _i++) {
            var _b = _a[_i], child = _b[0], panelEl = _b[1];
            panelEl.appendChild(this.child_views[child.id].el);
        }
    };
    return TabsView;
}(widget_1.WidgetView));
exports.TabsView = TabsView;
var Tabs = /** @class */ (function (_super) {
    tslib_1.__extends(Tabs, _super);
    function Tabs(attrs) {
        return _super.call(this, attrs) || this;
    }
    Tabs.initClass = function () {
        this.prototype.type = "Tabs";
        this.prototype.default_view = TabsView;
        this.define({
            tabs: [p.Array, []],
            active: [p.Number, 0],
            callback: [p.Instance],
        });
    };
    Tabs.prototype.get_layoutable_children = function () {
        return this.children;
    };
    Object.defineProperty(Tabs.prototype, "children", {
        get: function () {
            return this.tabs.map(function (tab) { return tab.child; });
        },
        enumerable: true,
        configurable: true
    });
    return Tabs;
}(widget_1.Widget));
exports.Tabs = Tabs;
Tabs.initClass();
