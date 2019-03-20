"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var logging_1 = require("core/logging");
var p = require("core/properties");
var layout_dom_1 = require("../layouts/layout_dom");
var WidgetBoxView = /** @class */ (function (_super) {
    tslib_1.__extends(WidgetBoxView, _super);
    function WidgetBoxView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WidgetBoxView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.children.change, function () { return _this.rebuild_child_views(); });
    };
    WidgetBoxView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-widget-box");
    };
    WidgetBoxView.prototype.render = function () {
        this._render_classes(); // XXX: because no super()
        if (this.model.sizing_mode == 'fixed' || this.model.sizing_mode == 'scale_height') {
            var width = this.get_width();
            if (this.model._width.value != width)
                this.solver.suggest_value(this.model._width, width);
        }
        if (this.model.sizing_mode == 'fixed' || this.model.sizing_mode == 'scale_width') {
            var height = this.get_height();
            if (this.model._height.value != height)
                this.solver.suggest_value(this.model._height, height);
        }
        this.solver.update_variables();
        if (this.model.sizing_mode == 'stretch_both') {
            this.el.style.position = 'absolute';
            this.el.style.left = this.model._dom_left.value + "px";
            this.el.style.top = this.model._dom_top.value + "px";
            this.el.style.width = this.model._width.value + "px";
            this.el.style.height = this.model._height.value + "px";
        }
        else {
            // Note we DO NOT want to set a height (except in stretch_both). Widgets
            // are happier sizing themselves. We've tried to tell the layout what
            // the height is with the suggest_value. But that doesn't mean we need
            // to put it in the dom.
            var css_width = void 0;
            if (this.model._width.value - 20 > 0)
                css_width = this.model._width.value - 20 + "px";
            else
                css_width = "100%";
            this.el.style.width = css_width;
        }
    };
    WidgetBoxView.prototype.get_height = function () {
        var height = 0;
        for (var key in this.child_views) {
            var child_view = this.child_views[key];
            var el = child_view.el;
            var style = getComputedStyle(el);
            var marginTop = parseInt(style.marginTop) || 0;
            var marginBottom = parseInt(style.marginBottom) || 0;
            height += el.offsetHeight + marginTop + marginBottom;
        }
        return height + 20;
    };
    WidgetBoxView.prototype.get_width = function () {
        if (this.model.width != null)
            return this.model.width;
        else {
            var width = this.el.scrollWidth + 20;
            for (var key in this.child_views) {
                var child_view = this.child_views[key];
                // Take the max width of all the children as the constrainer.
                var child_width = child_view.el.scrollWidth;
                if (child_width > width)
                    width = child_width;
            }
            return width;
        }
    };
    return WidgetBoxView;
}(layout_dom_1.LayoutDOMView));
exports.WidgetBoxView = WidgetBoxView;
var WidgetBox = /** @class */ (function (_super) {
    tslib_1.__extends(WidgetBox, _super);
    function WidgetBox(attrs) {
        return _super.call(this, attrs) || this;
    }
    WidgetBox.initClass = function () {
        this.prototype.type = "WidgetBox";
        this.prototype.default_view = WidgetBoxView;
        this.define({
            children: [p.Array, []],
        });
    };
    WidgetBox.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        if (this.sizing_mode == 'fixed' && this.width == null) {
            this.width = 300; // Set a default for fixed.
            logging_1.logger.info("WidgetBox mode is fixed, but no width specified. Using default of 300.");
        }
    };
    WidgetBox.prototype.get_constrained_variables = function () {
        var vars = tslib_1.__assign({}, _super.prototype.get_constrained_variables.call(this), { on_edge_align_top: this._top, on_edge_align_bottom: this._height_minus_bottom, on_edge_align_left: this._left, on_edge_align_right: this._width_minus_right, box_cell_align_top: this._top, box_cell_align_bottom: this._height_minus_bottom, box_cell_align_left: this._left, box_cell_align_right: this._width_minus_right, box_equal_size_top: this._top, box_equal_size_bottom: this._height_minus_bottom });
        if (this.sizing_mode != 'fixed') {
            vars.box_equal_size_left = this._left;
            vars.box_equal_size_right = this._width_minus_right;
        }
        return vars;
    };
    WidgetBox.prototype.get_layoutable_children = function () {
        return this.children;
    };
    return WidgetBox;
}(layout_dom_1.LayoutDOM));
exports.WidgetBox = WidgetBox;
WidgetBox.initClass();
