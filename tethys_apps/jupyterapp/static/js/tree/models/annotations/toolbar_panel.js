"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var build_views_1 = require("core/build_views");
var dom_1 = require("core/dom");
var p = require("core/properties");
var ToolbarPanelView = /** @class */ (function (_super) {
    tslib_1.__extends(ToolbarPanelView, _super);
    function ToolbarPanelView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ToolbarPanelView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.plot_view.canvas_events.appendChild(this.el);
        this._toolbar_views = {};
        build_views_1.build_views(this._toolbar_views, [this.model.toolbar], { parent: this });
    };
    ToolbarPanelView.prototype.remove = function () {
        build_views_1.remove_views(this._toolbar_views);
        _super.prototype.remove.call(this);
    };
    ToolbarPanelView.prototype.render = function () {
        _super.prototype.render.call(this);
        if (!this.model.visible) {
            dom_1.hide(this.el);
            return;
        }
        var panel = this.model.panel;
        this.el.style.position = "absolute";
        this.el.style.left = panel._left.value + "px";
        this.el.style.top = panel._top.value + "px";
        this.el.style.width = panel._width.value + "px";
        this.el.style.height = panel._height.value + "px";
        this.el.style.overflow = "hidden";
        var toolbar = this._toolbar_views[this.model.toolbar.id];
        toolbar.render();
        dom_1.empty(this.el);
        this.el.appendChild(toolbar.el);
        dom_1.show(this.el);
    };
    ToolbarPanelView.prototype._get_size = function () {
        return 30;
    };
    return ToolbarPanelView;
}(annotation_1.AnnotationView));
exports.ToolbarPanelView = ToolbarPanelView;
var ToolbarPanel = /** @class */ (function (_super) {
    tslib_1.__extends(ToolbarPanel, _super);
    function ToolbarPanel(attrs) {
        return _super.call(this, attrs) || this;
    }
    ToolbarPanel.initClass = function () {
        this.prototype.type = 'ToolbarPanel';
        this.prototype.default_view = ToolbarPanelView;
        this.define({
            toolbar: [p.Instance],
        });
    };
    return ToolbarPanel;
}(annotation_1.Annotation));
exports.ToolbarPanel = ToolbarPanel;
ToolbarPanel.initClass();
