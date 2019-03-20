"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var dom_1 = require("core/dom");
var p = require("core/properties");
var layout_canvas_1 = require("core/layout/layout_canvas");
var solver_1 = require("core/layout/solver");
var build_views_1 = require("core/build_views");
var dom_view_1 = require("core/dom_view");
var LayoutDOMView = /** @class */ (function (_super) {
    tslib_1.__extends(LayoutDOMView, _super);
    function LayoutDOMView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._solver_inited = false;
        _this._idle_notified = false;
        return _this;
    }
    LayoutDOMView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        // this is a root view
        if (this.is_root)
            this._solver = new solver_1.Solver();
        this.child_views = {};
        this.build_child_views();
    };
    LayoutDOMView.prototype.remove = function () {
        for (var model_id in this.child_views) {
            var view = this.child_views[model_id];
            view.remove();
        }
        this.child_views = {};
        // remove on_resize
        _super.prototype.remove.call(this);
    };
    LayoutDOMView.prototype.has_finished = function () {
        if (!_super.prototype.has_finished.call(this))
            return false;
        for (var model_id in this.child_views) {
            var child = this.child_views[model_id];
            if (!child.has_finished())
                return false;
        }
        return true;
    };
    LayoutDOMView.prototype.notify_finished = function () {
        if (!this.is_root)
            _super.prototype.notify_finished.call(this);
        else {
            if (!this._idle_notified && this.has_finished()) {
                if (this.model.document != null) {
                    this._idle_notified = true;
                    this.model.document.notify_idle(this.model);
                }
            }
        }
    };
    LayoutDOMView.prototype._calc_width_height = function () {
        var measuring = this.el;
        while (measuring = measuring.parentElement) {
            // .bk-root element doesn't bring any value
            if (measuring.classList.contains("bk-root"))
                continue;
            // we reached <body> element, so use viewport size
            if (measuring == document.body) {
                var _a = dom_1.margin(document.body), left_1 = _a.left, right_1 = _a.right, top_1 = _a.top, bottom_1 = _a.bottom;
                var width_1 = document.documentElement.clientWidth - left_1 - right_1;
                var height_1 = document.documentElement.clientHeight - top_1 - bottom_1;
                return [width_1, height_1];
            }
            // stop on first element with sensible dimensions
            var _b = dom_1.padding(measuring), left = _b.left, right = _b.right, top_2 = _b.top, bottom = _b.bottom;
            var _c = measuring.getBoundingClientRect(), width = _c.width, height = _c.height;
            var inner_width = width - left - right;
            var inner_height = height - top_2 - bottom;
            switch (this.model.sizing_mode) {
                case "scale_width": {
                    if (inner_width > 0)
                        return [inner_width, inner_height > 0 ? inner_height : null];
                    break;
                }
                case "scale_height": {
                    if (inner_height > 0)
                        return [inner_width > 0 ? inner_width : null, inner_height];
                    break;
                }
                case "scale_both":
                case "stretch_both": {
                    if (inner_width > 0 || inner_height > 0)
                        return [inner_width > 0 ? inner_width : null, inner_height > 0 ? inner_height : null];
                    break;
                }
                default:
                    throw new Error("unreachable");
            }
        }
        // this element is detached from DOM
        return [null, null];
    };
    LayoutDOMView.prototype._init_solver = function () {
        this._root_width = new solver_1.Variable(this.toString() + ".root_width");
        this._root_height = new solver_1.Variable(this.toString() + ".root_height");
        // XXX: this relies on the fact that missing `strength` argument results
        // in strength being NaN, which behaves like `Strength.required`. However,
        // this is banned by the API.
        this._solver.add_edit_variable(this._root_width, NaN);
        this._solver.add_edit_variable(this._root_height, NaN);
        var editables = this.model.get_all_editables();
        for (var _i = 0, editables_1 = editables; _i < editables_1.length; _i++) {
            var edit_variable = editables_1[_i];
            this._solver.add_edit_variable(edit_variable, solver_1.Strength.strong);
        }
        var constraints = this.model.get_all_constraints();
        for (var _a = 0, constraints_1 = constraints; _a < constraints_1.length; _a++) {
            var constraint = constraints_1[_a];
            this._solver.add_constraint(constraint);
        }
        var variables = this.model.get_constrained_variables();
        if (variables.width != null)
            this._solver.add_constraint(solver_1.EQ(variables.width, this._root_width));
        if (variables.height != null)
            this._solver.add_constraint(solver_1.EQ(variables.height, this._root_height));
        this._solver.update_variables();
        this._solver_inited = true;
    };
    LayoutDOMView.prototype._suggest_dims = function (width, height) {
        var _a;
        var variables = this.model.get_constrained_variables();
        if (variables.width != null || variables.height != null) {
            if (width == null || height == null)
                _a = this._calc_width_height(), width = _a[0], height = _a[1];
            if (variables.width != null && width != null)
                this._solver.suggest_value(this._root_width, width);
            if (variables.height != null && height != null)
                this._solver.suggest_value(this._root_height, height);
            this._solver.update_variables();
        }
    };
    LayoutDOMView.prototype.resize = function (width, height) {
        if (width === void 0) { width = null; }
        if (height === void 0) { height = null; }
        if (!this.is_root)
            this.root.resize(width, height);
        else
            this._do_layout(false, width, height);
    };
    LayoutDOMView.prototype.partial_layout = function () {
        if (!this.is_root)
            this.root.partial_layout();
        else
            this._do_layout(false);
    };
    LayoutDOMView.prototype.layout = function () {
        if (!this.is_root)
            this.root.layout();
        else
            this._do_layout(true);
    };
    LayoutDOMView.prototype._do_layout = function (full, width, height) {
        if (width === void 0) { width = null; }
        if (height === void 0) { height = null; }
        if (!this._solver_inited || full) {
            this._solver.clear();
            this._init_solver();
        }
        this._suggest_dims(width, height);
        // XXX: do layout twice, because there are interdependencies between views,
        // which currently cannot be resolved with one pass. The third one triggers
        // rendering and (expensive) painting.
        this._layout(); // layout (1)
        this._layout(); // layout (2)
        this._layout(true); // render & paint
        this.notify_finished();
    };
    LayoutDOMView.prototype._layout = function (final) {
        if (final === void 0) { final = false; }
        for (var _i = 0, _a = this.model.get_layoutable_children(); _i < _a.length; _i++) {
            var child = _a[_i];
            var child_view = this.child_views[child.id];
            if (child_view._layout != null)
                child_view._layout(final);
        }
        this.render();
        if (final)
            this._has_finished = true;
    };
    LayoutDOMView.prototype.rebuild_child_views = function () {
        this.solver.clear();
        this.build_child_views();
        this.layout();
    };
    LayoutDOMView.prototype.build_child_views = function () {
        var children = this.model.get_layoutable_children();
        build_views_1.build_views(this.child_views, children, { parent: this });
        dom_1.empty(this.el);
        for (var _i = 0, children_1 = children; _i < children_1.length; _i++) {
            var child = children_1[_i];
            // Look-up the child_view in this.child_views and then append We can't just
            // read from this.child_views because then we don't get guaranteed ordering.
            // Which is a problem in non-box layouts.
            var child_view = this.child_views[child.id];
            this.el.appendChild(child_view.el);
        }
    };
    LayoutDOMView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        if (this.is_root)
            window.addEventListener("resize", this);
        // XXX: this.connect(this.model.change, () => this.layout())
        this.connect(this.model.properties.sizing_mode.change, function () { return _this.layout(); });
    };
    LayoutDOMView.prototype.handleEvent = function () {
        this.resize();
    };
    LayoutDOMView.prototype.disconnect_signals = function () {
        window.removeEventListener("resize", this);
        _super.prototype.disconnect_signals.call(this);
    };
    LayoutDOMView.prototype._render_classes = function () {
        this.el.className = ""; // removes all classes
        for (var _i = 0, _a = this.css_classes(); _i < _a.length; _i++) {
            var name_1 = _a[_i];
            this.el.classList.add(name_1);
        }
        this.el.classList.add("bk-layout-" + this.model.sizing_mode);
        for (var _b = 0, _c = this.model.css_classes; _b < _c.length; _b++) {
            var cls = _c[_b];
            this.el.classList.add(cls);
        }
    };
    LayoutDOMView.prototype.render = function () {
        this._render_classes();
        switch (this.model.sizing_mode) {
            case "fixed": {
                // If the width or height is unset:
                // - compute it from children
                // - but then save for future use
                // (for some reason widget boxes keep shrinking if you keep computing
                // but this is more efficient and appropriate for fixed anyway).
                var width = void 0;
                if (this.model.width != null)
                    width = this.model.width;
                else
                    width = this.get_width();
                this.model.setv({ width: width }, { silent: true });
                var height = void 0;
                if (this.model.height != null)
                    height = this.model.height;
                else
                    height = this.get_height();
                this.model.setv({ height: height }, { silent: true });
                this.solver.suggest_value(this.model._width, width);
                this.solver.suggest_value(this.model._height, height);
                break;
            }
            case "scale_width": {
                var height = this.get_height();
                this.solver.suggest_value(this.model._height, height);
                break;
            }
            case "scale_height": {
                var width = this.get_width();
                this.solver.suggest_value(this.model._width, width);
                break;
            }
            case "scale_both": {
                var _a = this.get_width_height(), width = _a[0], height = _a[1];
                this.solver.suggest_value(this.model._width, width);
                this.solver.suggest_value(this.model._height, height);
                break;
            }
        }
        this.solver.update_variables();
        this.position();
    };
    LayoutDOMView.prototype.position = function () {
        switch (this.model.sizing_mode) {
            case "fixed":
            case "scale_width":
            case "scale_height": {
                this.el.style.position = "relative";
                this.el.style.left = "";
                this.el.style.top = "";
                break;
            }
            case "scale_both":
            case "stretch_both": {
                this.el.style.position = "absolute";
                this.el.style.left = this.model._dom_left.value + "px";
                this.el.style.top = this.model._dom_top.value + "px";
                break;
            }
        }
        this.el.style.width = this.model._width.value + "px";
        this.el.style.height = this.model._height.value + "px";
    };
    LayoutDOMView.prototype.get_width_height = function () {
        /**
         * Fit into enclosing DOM and preserve original aspect.
         */
        var _a = this._calc_width_height(), parent_width = _a[0], parent_height = _a[1];
        if (parent_width == null && parent_height == null)
            throw new Error("detached element");
        var ar = this.model.get_aspect_ratio();
        if (parent_width != null && parent_height == null)
            return [parent_width, parent_width / ar];
        if (parent_width == null && parent_height != null)
            return [parent_height * ar, parent_height];
        var new_width_1 = parent_width;
        var new_height_1 = parent_width / ar;
        var new_width_2 = parent_height * ar;
        var new_height_2 = parent_height;
        var width;
        var height;
        if (new_width_1 < new_width_2) {
            width = new_width_1;
            height = new_height_1;
        }
        else {
            width = new_width_2;
            height = new_height_2;
        }
        return [width, height];
    };
    return LayoutDOMView;
}(dom_view_1.DOMView));
exports.LayoutDOMView = LayoutDOMView;
var LayoutDOM = /** @class */ (function (_super) {
    tslib_1.__extends(LayoutDOM, _super);
    function LayoutDOM(attrs) {
        return _super.call(this, attrs) || this;
    }
    LayoutDOM.initClass = function () {
        this.prototype.type = "LayoutDOM";
        this.define({
            height: [p.Number],
            width: [p.Number],
            disabled: [p.Bool, false],
            sizing_mode: [p.SizingMode, "fixed"],
            css_classes: [p.Array, []],
        });
    };
    LayoutDOM.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._width = new solver_1.Variable(this.toString() + ".width");
        this._height = new solver_1.Variable(this.toString() + ".height");
        this._left = new solver_1.Variable(this.toString() + ".left");
        this._right = new solver_1.Variable(this.toString() + ".right");
        this._top = new solver_1.Variable(this.toString() + ".top");
        this._bottom = new solver_1.Variable(this.toString() + ".bottom");
        this._dom_top = new solver_1.Variable(this.toString() + ".dom_top");
        this._dom_left = new solver_1.Variable(this.toString() + ".dom_left");
        this._width_minus_right = new solver_1.Variable(this.toString() + ".width_minus_right");
        this._height_minus_bottom = new solver_1.Variable(this.toString() + ".height_minus_bottom");
        this._whitespace_top = new solver_1.Variable(this.toString() + ".whitespace_top");
        this._whitespace_bottom = new solver_1.Variable(this.toString() + ".whitespace_bottom");
        this._whitespace_left = new solver_1.Variable(this.toString() + ".whitespace_left");
        this._whitespace_right = new solver_1.Variable(this.toString() + ".whitespace_right");
    };
    Object.defineProperty(LayoutDOM.prototype, "layout_bbox", {
        get: function () {
            return {
                top: this._top.value,
                left: this._left.value,
                width: this._width.value,
                height: this._height.value,
                right: this._right.value,
                bottom: this._bottom.value,
                dom_top: this._dom_top.value,
                dom_left: this._dom_left.value,
            };
        },
        enumerable: true,
        configurable: true
    });
    LayoutDOM.prototype.dump_layout = function () {
        var layoutables = {};
        var pending = [this];
        var obj;
        while (obj = pending.shift()) {
            pending.push.apply(pending, obj.get_layoutable_children());
            layoutables[obj.toString()] = obj.layout_bbox;
        }
        console.table(layoutables);
    };
    LayoutDOM.prototype.get_all_constraints = function () {
        var constraints = this.get_constraints();
        for (var _i = 0, _a = this.get_layoutable_children(); _i < _a.length; _i++) {
            var child = _a[_i];
            if (child instanceof layout_canvas_1.LayoutCanvas)
                constraints = constraints.concat(child.get_constraints());
            else
                constraints = constraints.concat(child.get_all_constraints());
        }
        return constraints;
    };
    LayoutDOM.prototype.get_all_editables = function () {
        var editables = this.get_editables();
        for (var _i = 0, _a = this.get_layoutable_children(); _i < _a.length; _i++) {
            var child = _a[_i];
            if (child instanceof layout_canvas_1.LayoutCanvas)
                editables = editables.concat(child.get_editables());
            else
                editables = editables.concat(child.get_all_editables());
        }
        return editables;
    };
    LayoutDOM.prototype.get_constraints = function () {
        return [
            // Make sure things dont squeeze out of their bounding box
            solver_1.GE(this._dom_left),
            solver_1.GE(this._dom_top),
            // Plot has to be inside the width/height
            solver_1.GE(this._left),
            solver_1.GE(this._width, [-1, this._right]),
            solver_1.GE(this._top),
            solver_1.GE(this._height, [-1, this._bottom]),
            // Declare computed constraints
            solver_1.EQ(this._width_minus_right, [-1, this._width], this._right),
            solver_1.EQ(this._height_minus_bottom, [-1, this._height], this._bottom),
        ];
    };
    LayoutDOM.prototype.get_layoutable_children = function () {
        return [];
    };
    LayoutDOM.prototype.get_editables = function () {
        switch (this.sizing_mode) {
            case "fixed":
                return [this._height, this._width];
            case "scale_width":
                return [this._height];
            case "scale_height":
                return [this._width];
            case "scale_both":
                return [this._width, this._height];
            default:
                return [];
        }
    };
    LayoutDOM.prototype.get_constrained_variables = function () {
        /*
         * THE FOLLOWING ARE OPTIONAL VARS THAT
         * YOU COULD ADD INTO SUBCLASSES
         *
         *  # When this widget is on the edge of a box visually,
         *  # align these variables down that edge. Right/bottom
         *  # are an inset from the edge.
         *  on_edge_align_top    : this._top
         *  on_edge_align_bottom : this._height_minus_bottom
         *  on_edge_align_left   : this._left
         *  on_edge_align_right  : this._width_minus_right
         *  # When this widget is in a box cell with the same "arity
         *  # path" as a widget in another cell, align these variables
         *  # between the two box cells. Right/bottom are an inset from
         *  # the edge.
         *  box_cell_align_top   : this._top
         *  box_cell_align_bottom: this._height_minus_bottom
         *  box_cell_align_left  : this._left
         *  box_cell_align_right : this._width_minus_right
         *  # When this widget is in a box, make these the same distance
         *  # apart in every widget. Right/bottom are inset from the edge.
         *  box_equal_size_top   : this._top
         *  box_equal_size_bottom: this._height_minus_bottom
         *  box_equal_size_left  : this._left
         *  box_equal_size_right : this._width_minus_right
         */
        var vars = {
            origin_x: this._dom_left,
            origin_y: this._dom_top,
            whitespace_top: this._whitespace_top,
            whitespace_bottom: this._whitespace_bottom,
            whitespace_left: this._whitespace_left,
            whitespace_right: this._whitespace_right,
        };
        switch (this.sizing_mode) {
            case "stretch_both":
                vars.width = this._width;
                vars.height = this._height;
                break;
            case "scale_width":
                vars.width = this._width;
                break;
            case "scale_height":
                vars.height = this._height;
                break;
        }
        return vars;
    };
    LayoutDOM.prototype.get_aspect_ratio = function () {
        return this.width / this.height;
    };
    return LayoutDOM;
}(model_1.Model));
exports.LayoutDOM = LayoutDOM;
LayoutDOM.initClass();
