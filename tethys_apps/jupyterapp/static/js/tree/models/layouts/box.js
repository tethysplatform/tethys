"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var solver_1 = require("core/layout/solver");
var p = require("core/properties");
var array_1 = require("core/util/array");
var layout_dom_1 = require("./layout_dom");
var BoxView = /** @class */ (function (_super) {
    tslib_1.__extends(BoxView, _super);
    function BoxView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BoxView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.children.change, function () { return _this.rebuild_child_views(); });
    };
    BoxView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-grid");
    };
    BoxView.prototype.get_height = function () {
        var children = this.model.get_layoutable_children();
        var child_heights = children.map(function (child) { return child._height.value; });
        var height;
        if (this.model._horizontal)
            height = array_1.max(child_heights);
        else
            height = array_1.sum(child_heights);
        return height;
    };
    BoxView.prototype.get_width = function () {
        var children = this.model.get_layoutable_children();
        var child_widths = children.map(function (child) { return child._width.value; });
        var width;
        if (this.model._horizontal)
            width = array_1.sum(child_widths);
        else
            width = array_1.max(child_widths);
        return width;
    };
    return BoxView;
}(layout_dom_1.LayoutDOMView));
exports.BoxView = BoxView;
var Box = /** @class */ (function (_super) {
    tslib_1.__extends(Box, _super);
    function Box(attrs) {
        return _super.call(this, attrs) || this;
    }
    Box.initClass = function () {
        this.prototype.type = "Box";
        this.prototype.default_view = BoxView;
        this.define({
            children: [p.Array, []],
        });
        this.internal({
            spacing: [p.Number, 6],
        });
    };
    Box.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._child_equal_size_width = new solver_1.Variable(this.toString() + ".child_equal_size_width");
        this._child_equal_size_height = new solver_1.Variable(this.toString() + ".child_equal_size_height");
        this._box_equal_size_top = new solver_1.Variable(this.toString() + ".box_equal_size_top");
        this._box_equal_size_bottom = new solver_1.Variable(this.toString() + ".box_equal_size_bottom");
        this._box_equal_size_left = new solver_1.Variable(this.toString() + ".box_equal_size_left");
        this._box_equal_size_right = new solver_1.Variable(this.toString() + ".box_equal_size_right");
        this._box_cell_align_top = new solver_1.Variable(this.toString() + ".box_cell_align_top");
        this._box_cell_align_bottom = new solver_1.Variable(this.toString() + ".box_cell_align_bottom");
        this._box_cell_align_left = new solver_1.Variable(this.toString() + ".box_cell_align_left");
        this._box_cell_align_right = new solver_1.Variable(this.toString() + ".box_cell_align_right");
    };
    Box.prototype.get_layoutable_children = function () {
        return this.children;
    };
    Box.prototype.get_constrained_variables = function () {
        return tslib_1.__assign({}, _super.prototype.get_constrained_variables.call(this), { box_equal_size_top: this._box_equal_size_top, box_equal_size_bottom: this._box_equal_size_bottom, box_equal_size_left: this._box_equal_size_left, box_equal_size_right: this._box_equal_size_right, box_cell_align_top: this._box_cell_align_top, box_cell_align_bottom: this._box_cell_align_bottom, box_cell_align_left: this._box_cell_align_left, box_cell_align_right: this._box_cell_align_right });
    };
    Box.prototype.get_constraints = function () {
        var constraints = _super.prototype.get_constraints.call(this);
        var add = function () {
            var new_constraints = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                new_constraints[_i] = arguments[_i];
            }
            constraints.push.apply(constraints, new_constraints);
        };
        var children = this.get_layoutable_children();
        if (children.length == 0)
            // No need to continue further if there are no children. Children sure do
            // make life a lot more complicated.
            return constraints;
        for (var _i = 0, children_1 = children; _i < children_1.length; _i++) {
            var child = children_1[_i];
            var vars_1 = child.get_constrained_variables();
            // Make total widget sizes fill the orthogonal direction
            // TODO(bird) Can't we make this shorter by using span which has already picked a
            // dominant direction (we'd just also need to set a doc_span)
            var rect = this._child_rect(vars_1);
            if (this._horizontal) {
                if (vars_1.height != null)
                    add(solver_1.EQ(rect.height, [-1, this._height]));
            }
            else {
                if (vars_1.width != null)
                    add(solver_1.EQ(rect.width, [-1, this._width]));
            }
            // Add equal_size constraint
            // - A child's "interesting area" (like the plot area) is the same size as the previous child
            //   (a child can opt out of this by not returning the box_equal_size variables)
            if (this._horizontal) {
                if (vars_1.box_equal_size_left != null && vars_1.box_equal_size_right != null && vars_1.width != null)
                    add(solver_1.EQ([-1, vars_1.box_equal_size_left], [-1, vars_1.box_equal_size_right], vars_1.width, this._child_equal_size_width));
            }
            else {
                if (vars_1.box_equal_size_top != null && vars_1.box_equal_size_bottom != null && vars_1.height != null)
                    add(solver_1.EQ([-1, vars_1.box_equal_size_top], [-1, vars_1.box_equal_size_bottom], vars_1.height, this._child_equal_size_height));
            }
        }
        // TODO(bird) - This is the second time we loop through children
        var last = this._info(children[0].get_constrained_variables());
        add(solver_1.EQ(last.span.start, 0));
        for (var i = 1; i < children.length; i++) {
            var next = this._info(children[i].get_constrained_variables());
            // Each child's start equals the previous child's end (unless we have a fixed layout
            // in which case size may not be available)
            if (last.span.size)
                add(solver_1.EQ(last.span.start, last.span.size, [-1, next.span.start]));
            // The whitespace at end of one child + start of next must equal the box spacing.
            // This must be a weak constraint because it can conflict with aligning the
            // alignable edges in each child. Alignment is generally more important visually than spacing.
            add(solver_1.WEAK_EQ(last.whitespace.after, next.whitespace.before, 0 - this.spacing));
            // If we can't satisfy the whitespace being equal to box spacing, we should fix
            // it (align things) by increasing rather than decreasing the whitespace.
            add(solver_1.GE(last.whitespace.after, next.whitespace.before, 0 - this.spacing));
            last = next;
        }
        // Child's side has to stick to the end of the box
        var vars = children[children.length - 1].get_constrained_variables();
        if (this._horizontal) {
            if (vars.width != null)
                add(solver_1.EQ(last.span.start, last.span.size, [-1, this._width]));
        }
        else {
            if (vars.height != null)
                add(solver_1.EQ(last.span.start, last.span.size, [-1, this._height]));
        }
        constraints = constraints.concat(
        // align outermost edges in both dimensions
        this._align_outer_edges_constraints(true), // horizontal=true
        this._align_outer_edges_constraints(false), 
        // line up edges in same_arity boxes
        this._align_inner_cell_edges_constraints(), 
        // build our equal_size bounds from the child ones
        this._box_equal_size_bounds(true), // horizontal=true
        this._box_equal_size_bounds(false), 
        // propagate cell alignment (between same_arity boxes) up the hierarchy
        this._box_cell_align_bounds(true), // horizontal=true
        this._box_cell_align_bounds(false), 
        // build our whitespace from the child ones
        this._box_whitespace(true), // horizontal=true
        this._box_whitespace(false));
        return constraints;
    };
    Box.prototype._child_rect = function (vars) {
        return {
            x: vars.origin_x,
            y: vars.origin_y,
            width: vars.width,
            height: vars.height,
        };
    };
    Box.prototype._span = function (rect) {
        // return [coordinate, size] pair in box_aligned direction
        if (this._horizontal)
            return { start: rect.x, size: rect.width };
        else
            return { start: rect.y, size: rect.height };
    };
    Box.prototype._info = function (vars) {
        var whitespace;
        if (this._horizontal)
            whitespace = { before: vars.whitespace_left, after: vars.whitespace_right };
        else
            whitespace = { before: vars.whitespace_top, after: vars.whitespace_bottom };
        var span = this._span(this._child_rect(vars));
        return { span: span, whitespace: whitespace };
    };
    Box.prototype._flatten_cell_edge_variables = function (horizontal) {
        /*
         * All alignment happens in terms of the
         * box_cell_align_{left,right,top,bottom} variables. We add
         * "path" information to variables so we know which ones align,
         * where the "path" includes the box arity and box cell we went
         * through.
         *
         * If we have a row of three plots, we should align the top and
         * bottom variables between the three plots.
         *
         * The flattened dictionary in this case (for the top and left
         * only) should be:
         *
         *   box_cell_align_top : [ 3 vars ]
         *   box_cell_align_bottom : [ 3 vars ]
         *
         * We don't do left/right starting from a row, and left/right
         * edges have nothing to align with here.
         *
         * Now say we have a row of three columns, each with three
         * plots (3x3 = 9). We should align the top/bottom variables
         * across the top three, middle three, and bottom three plots,
         * as if those groupings were rows. We do this by flattening
         * starting from the row first, which gets us a dictionary only
         * of top/bottom variables.
         *
         *   box_cell_align_top col-3-0- : [ 3 plots from top of columns ]
         *   box_cell_align_top col-3-1- : [ 3 plots from middle of columns ]
         *   box_cell_align_top col-3-2- : [ 3 plots from bottom of columns ]
         *
         * "col-3-1-" = 3-cell column, cell index 1.
         *
         * In three later, separate calls to
         * _align_inner_cell_edges_constraints() on each column, we'll
         * get the left/right variables:
         *
         *   box_cell_align_left : [ 3 left-column plots ]
         *   box_cell_align_left : [ 3 middle-column plots ]
         *   box_cell_align_left : [ 3 right-column plots ]
         *
         * Now add another nesting - we have a row of three columns,
         * each with three rows, each with three plots. This is
         * arranged 3x9 = 27.
         *
         *   box_cell_align_top col-3-0- : [ 9 plots from top rows of columns ]
         *   box_cell_align_top col-3-1- : [ 9 plots from middle rows of columns ]
         *   box_cell_align_top col-3-2- : [ 9 plots from bottom rows of columns ]
         *
         * When we make the _align_inner_cell_edges_constraints() calls on each of the three
         * columns, each column will return row-pathed values
         *
         *   box_cell_align_left row-3-0-: [  3 plots in left column of left column ]
         *   box_cell_align_left row-3-1-: [  3 plots in middle column of left column ]
         *   box_cell_align_left row-3-2-: [  3 plots in right column of left column ]
         *   ... same for the middle and right columns
         *
         * Anyway in essence what we do is that we add only rows to the
         * path to left/right variables, and only columns to the path
         * to top/bottom variables.
         *
         * If we nest yet another level we would finally get paths with
         * multiple rows or multiple columns in them.
         */
        var relevant_edges;
        if (horizontal)
            relevant_edges = Box._top_bottom_inner_cell_edge_variables;
        else
            relevant_edges = Box._left_right_inner_cell_edge_variables;
        var add_path = horizontal != this._horizontal;
        var children = this.get_layoutable_children();
        var arity = children.length;
        var flattened = {};
        var cell = 0;
        for (var _i = 0, children_2 = children; _i < children_2.length; _i++) {
            var child = children_2[_i];
            var cell_vars = void 0;
            if (child instanceof Box)
                cell_vars = child._flatten_cell_edge_variables(horizontal);
            else
                cell_vars = {};
            var all_vars = child.get_constrained_variables();
            for (var _a = 0, relevant_edges_1 = relevant_edges; _a < relevant_edges_1.length; _a++) {
                var name_1 = relevant_edges_1[_a];
                if (name_1 in all_vars)
                    cell_vars[name_1] = [all_vars[name_1]];
            }
            for (var key in cell_vars) {
                var variables = cell_vars[key];
                var new_key = void 0;
                if (add_path) {
                    var parsed = key.split(" ");
                    var kind = parsed[0];
                    var path = parsed.length > 1 ? parsed[1] : "";
                    var direction = this._horizontal ? "row" : "col";
                    // TODO should we "ignore" arity-1 boxes potentially by not adding a path suffix?
                    new_key = kind + " " + direction + "-" + arity + "-" + cell + "-" + path;
                }
                else
                    new_key = key;
                if (new_key in flattened)
                    flattened[new_key] = flattened[new_key].concat(variables);
                else
                    flattened[new_key] = variables;
            }
            cell++;
        }
        return flattened;
    };
    // This should only be called on the toplevel box (twice,
    // once with horizontal=true and once with horizontal=false)
    Box.prototype._align_inner_cell_edges_constraints = function () {
        var constraints = [];
        // XXX: checking for `this.document?` is a temporary hack, because document isn't always
        // attached properly. However, if document is not attached then we know it can't be
        // a root, because otherwise add_root() would attach it. All this layout logic should
        // be part of views instead of models and use is_root, etc.
        if (this.document != null && array_1.includes(this.document.roots(), this)) {
            var flattened = this._flatten_cell_edge_variables(this._horizontal);
            for (var key in flattened) {
                var variables = flattened[key];
                if (variables.length > 1) {
                    //console.log("constraining ", key, " ", variables)
                    var last = variables[0];
                    for (var i = 1; i < variables.length; i++)
                        constraints.push(solver_1.EQ(variables[i], [-1, last]));
                }
            }
        }
        return constraints;
    };
    // returns a two-item array where each item is a list of edge
    // children from the start and end respectively
    Box.prototype._find_edge_leaves = function (horizontal) {
        var children = this.get_layoutable_children();
        // console.log(`  finding edge leaves in ${children.length}-${this.type}, ` +
        //  `our orientation ${this._horizontal} finding ${horizontal} children `, children)
        var leaves = [[], []];
        if (children.length > 0) {
            if (this._horizontal == horizontal) {
                // note start and end may be the same
                var start = children[0];
                var end = children[children.length - 1];
                if (start instanceof Box)
                    leaves[0] = leaves[0].concat(start._find_edge_leaves(horizontal)[0]);
                else
                    leaves[0].push(start);
                if (end instanceof Box)
                    leaves[1] = leaves[1].concat(end._find_edge_leaves(horizontal)[1]);
                else
                    leaves[1].push(end);
            }
            else {
                // if we are a column and someone wants the horizontal edges,
                // we return the horizontal edges from all of our children
                for (var _i = 0, children_3 = children; _i < children_3.length; _i++) {
                    var child = children_3[_i];
                    if (child instanceof Box) {
                        var child_leaves = child._find_edge_leaves(horizontal);
                        leaves[0] = leaves[0].concat(child_leaves[0]);
                        leaves[1] = leaves[1].concat(child_leaves[1]);
                    }
                    else {
                        leaves[0].push(child);
                        leaves[1].push(child);
                    }
                }
            }
        }
        // console.log("  start leaves ", leaves[0].map((leaf) -> leaf.id)
        // console.log("  end leaves ", leaves[1].map((leaf) -> leaf.id)
        return leaves;
    };
    Box.prototype._align_outer_edges_constraints = function (horizontal) {
        // console.log(`${if horizontal then 'horizontal' else 'vertical'} outer edge constraints in ${this.get_layoutable_children().length}-${this.type}`)
        var _a = this._find_edge_leaves(horizontal), start_leaves = _a[0], end_leaves = _a[1];
        var start_variable;
        var end_variable;
        if (horizontal) {
            start_variable = 'on_edge_align_left';
            end_variable = 'on_edge_align_right';
        }
        else {
            start_variable = 'on_edge_align_top';
            end_variable = 'on_edge_align_bottom';
        }
        var collect_vars = function (leaves, name) {
            //console.log(`collecting ${name} in `, leaves)
            var edges = [];
            for (var _i = 0, leaves_1 = leaves; _i < leaves_1.length; _i++) {
                var leaf = leaves_1[_i];
                var vars = leaf.get_constrained_variables();
                if (name in vars)
                    edges.push(vars[name]);
                //vars[name]['_debug'] = `${name} from ${leaf.id}`
            }
            return edges;
        };
        var start_edges = collect_vars(start_leaves, start_variable);
        var end_edges = collect_vars(end_leaves, end_variable);
        var result = [];
        var add_all_equal = function (edges) {
            if (edges.length > 1) {
                var first = edges[0];
                for (var i = 1; i < edges.length; i++) {
                    var edge = edges[i];
                    //console.log(`  constraining ${first._debug} == ${edge._debug}`)
                    result.push(solver_1.EQ([-1, first], edge));
                }
            }
        };
        add_all_equal(start_edges);
        add_all_equal(end_edges);
        // console.log("computed constraints ", result)
        return result;
    };
    Box.prototype._box_insets_from_child_insets = function (horizontal, child_variable_prefix, our_variable_prefix, minimum) {
        var _a = this._find_edge_leaves(horizontal), start_leaves = _a[0], end_leaves = _a[1];
        var start_variable;
        var end_variable;
        var our_start;
        var our_end;
        if (horizontal) {
            start_variable = child_variable_prefix + "_left";
            end_variable = child_variable_prefix + "_right";
            our_start = this[our_variable_prefix + "_left"];
            our_end = this[our_variable_prefix + "_right"];
        }
        else {
            start_variable = child_variable_prefix + "_top";
            end_variable = child_variable_prefix + "_bottom";
            our_start = this[our_variable_prefix + "_top"];
            our_end = this[our_variable_prefix + "_bottom"];
        }
        var result = [];
        var add_constraints = function (ours, leaves, name) {
            for (var _i = 0, leaves_2 = leaves; _i < leaves_2.length; _i++) {
                var leaf = leaves_2[_i];
                var vars = leaf.get_constrained_variables();
                if (name in vars) {
                    if (minimum)
                        result.push(solver_1.GE([-1, ours], vars[name]));
                    else
                        result.push(solver_1.EQ([-1, ours], vars[name]));
                }
            }
        };
        add_constraints(our_start, start_leaves, start_variable);
        add_constraints(our_end, end_leaves, end_variable);
        return result;
    };
    Box.prototype._box_equal_size_bounds = function (horizontal) {
        // false = box bounds equal all outer child bounds exactly
        return this._box_insets_from_child_insets(horizontal, 'box_equal_size', '_box_equal_size', false);
    };
    Box.prototype._box_cell_align_bounds = function (horizontal) {
        // false = box bounds equal all outer child bounds exactly
        return this._box_insets_from_child_insets(horizontal, 'box_cell_align', '_box_cell_align', false);
    };
    Box.prototype._box_whitespace = function (horizontal) {
        // true = box whitespace must be the minimum of child
        // whitespaces (i.e. distance from box edge to the outermost
        // child pixels)
        return this._box_insets_from_child_insets(horizontal, 'whitespace', '_whitespace', true);
    };
    Box._left_right_inner_cell_edge_variables = ['box_cell_align_left', 'box_cell_align_right'];
    Box._top_bottom_inner_cell_edge_variables = ['box_cell_align_top', 'box_cell_align_bottom'];
    return Box;
}(layout_dom_1.LayoutDOM));
exports.Box = Box;
Box.initClass();
