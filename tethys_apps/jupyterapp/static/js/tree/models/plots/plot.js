"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var solver_1 = require("core/layout/solver");
var logging_1 = require("core/logging");
var p = require("core/properties");
var signaling_1 = require("core/signaling");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
var layout_dom_1 = require("../layouts/layout_dom");
var title_1 = require("../annotations/title");
var linear_scale_1 = require("../scales/linear_scale");
var toolbar_1 = require("../tools/toolbar");
var toolbar_panel_1 = require("../annotations/toolbar_panel");
var plot_canvas_1 = require("./plot_canvas");
var column_data_source_1 = require("../sources/column_data_source");
var glyph_renderer_1 = require("../renderers/glyph_renderer");
var bokeh_events_1 = require("core/bokeh_events");
var data_range1d_1 = require("../ranges/data_range1d");
var PlotView = /** @class */ (function (_super) {
    tslib_1.__extends(PlotView, _super);
    function PlotView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PlotView.prototype.connect_signals = function () {
        _super.prototype.connect_signals.call(this);
        // Note: Title object cannot be replaced after initialization, similar to axes, and also
        // not being able to change the sizing_mode. All of these changes require a re-initialization
        // of all constraints which we don't currently support.
        var title_msg = "Title object cannot be replaced. Try changing properties on title to update it after initialization.";
        this.connect(this.model.properties.title.change, function () { return logging_1.logger.warn(title_msg); });
    };
    PlotView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-plot-layout");
    };
    PlotView.prototype.get_height = function () {
        return this.model._width.value / this.model.get_aspect_ratio();
    };
    PlotView.prototype.get_width = function () {
        return this.model._height.value * this.model.get_aspect_ratio();
    };
    PlotView.prototype.save = function (name) {
        this.plot_canvas_view.save(name);
    };
    Object.defineProperty(PlotView.prototype, "plot_canvas_view", {
        get: function () {
            // XXX: PlotCanvasView is not LayoutDOMView
            return this.child_views[this.model.plot_canvas.id];
        },
        enumerable: true,
        configurable: true
    });
    return PlotView;
}(layout_dom_1.LayoutDOMView));
exports.PlotView = PlotView;
var Plot = /** @class */ (function (_super) {
    tslib_1.__extends(Plot, _super);
    function Plot(attrs) {
        return _super.call(this, attrs) || this;
    }
    Plot.initClass = function () {
        this.prototype.type = "Plot";
        this.prototype.default_view = PlotView;
        this.mixins(["line:outline_", "fill:background_", "fill:border_"]);
        this.define({
            toolbar: [p.Instance, function () { return new toolbar_1.Toolbar(); }],
            toolbar_location: [p.Location, 'right'],
            toolbar_sticky: [p.Boolean, true],
            plot_width: [p.Number, 600],
            plot_height: [p.Number, 600],
            title: [p.Any, function () { return new title_1.Title({ text: "" }); }],
            title_location: [p.Location, 'above'],
            h_symmetry: [p.Bool, true],
            v_symmetry: [p.Bool, false],
            above: [p.Array, []],
            below: [p.Array, []],
            left: [p.Array, []],
            right: [p.Array, []],
            renderers: [p.Array, []],
            x_range: [p.Instance, function () { return new data_range1d_1.DataRange1d(); }],
            extra_x_ranges: [p.Any, {}],
            y_range: [p.Instance, function () { return new data_range1d_1.DataRange1d(); }],
            extra_y_ranges: [p.Any, {}],
            x_scale: [p.Instance, function () { return new linear_scale_1.LinearScale(); }],
            y_scale: [p.Instance, function () { return new linear_scale_1.LinearScale(); }],
            lod_factor: [p.Number, 10],
            lod_interval: [p.Number, 300],
            lod_threshold: [p.Number, 2000],
            lod_timeout: [p.Number, 500],
            hidpi: [p.Bool, true],
            output_backend: [p.OutputBackend, "canvas"],
            min_border: [p.Number, 5],
            min_border_top: [p.Number, null],
            min_border_left: [p.Number, null],
            min_border_bottom: [p.Number, null],
            min_border_right: [p.Number, null],
            inner_width: [p.Number],
            inner_height: [p.Number],
            layout_width: [p.Number],
            layout_height: [p.Number],
            match_aspect: [p.Bool, false],
            aspect_scale: [p.Number, 1],
        });
        this.override({
            outline_line_color: "#e5e5e5",
            border_fill_color: "#ffffff",
            background_fill_color: "#ffffff",
        });
        bokeh_events_1.register_with_event(bokeh_events_1.UIEvent, this);
    };
    Plot.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.reset = new signaling_1.Signal0(this, "reset");
        for (var _i = 0, _a = object_1.values(this.extra_x_ranges).concat(this.x_range); _i < _a.length; _i++) {
            var xr = _a[_i];
            var plots = xr.plots;
            if (types_1.isArray(plots)) {
                plots = plots.concat(this);
                xr.setv({ plots: plots }, { silent: true });
            }
        }
        for (var _b = 0, _c = object_1.values(this.extra_y_ranges).concat(this.y_range); _b < _c.length; _b++) {
            var yr = _c[_b];
            var plots = yr.plots;
            if (types_1.isArray(plots)) {
                plots = plots.concat(this);
                yr.setv({ plots: plots }, { silent: true });
            }
        }
        // Min border applies to the edge of everything
        if (this.min_border != null) {
            if (this.min_border_top == null)
                this.min_border_top = this.min_border;
            if (this.min_border_bottom == null)
                this.min_border_bottom = this.min_border;
            if (this.min_border_left == null)
                this.min_border_left = this.min_border;
            if (this.min_border_right == null)
                this.min_border_right = this.min_border;
        }
        // Setup side renderers
        for (var _d = 0, _e = ['above', 'below', 'left', 'right']; _d < _e.length; _d++) {
            var side = _e[_d];
            var layout_renderers = this.getv(side);
            for (var _f = 0, layout_renderers_1 = layout_renderers; _f < layout_renderers_1.length; _f++) {
                var renderer = layout_renderers_1[_f];
                renderer.add_panel(side);
            }
        }
        this._init_title_panel();
        this._init_toolbar_panel();
        this._plot_canvas = this._init_plot_canvas();
        this.plot_canvas.toolbar = this.toolbar;
        // Set width & height to be the passed in plot_width and plot_height
        // We may need to be more subtle about this - not sure why people use one
        // or the other.
        if (this.width == null)
            this.width = this.plot_width;
        if (this.height == null)
            this.height = this.plot_height;
    };
    Plot.prototype._init_plot_canvas = function () {
        return new plot_canvas_1.PlotCanvas({ plot: this });
    };
    Plot.prototype._init_title_panel = function () {
        if (this.title != null) {
            var title = types_1.isString(this.title) ? new title_1.Title({ text: this.title }) : this.title;
            this.add_layout(title, this.title_location);
        }
    };
    Plot.prototype._init_toolbar_panel = function () {
        var _this = this;
        var tpanel = array_1.find(this.renderers, function (model) {
            return model instanceof toolbar_panel_1.ToolbarPanel && array_1.includes(model.tags, _this.id);
        });
        if (tpanel != null)
            this.remove_layout(tpanel);
        switch (this.toolbar_location) {
            case "left":
            case "right":
            case "above":
            case "below": {
                tpanel = new toolbar_panel_1.ToolbarPanel({ toolbar: this.toolbar, tags: [this.id] });
                this.toolbar.toolbar_location = this.toolbar_location;
                if (this.toolbar_sticky) {
                    var models = this.getv(this.toolbar_location);
                    var title = array_1.find(models, function (model) { return model instanceof title_1.Title; });
                    if (title != null) {
                        tpanel.set_panel(title.panel); // XXX, XXX: because find() doesn't provide narrowed types
                        this.add_renderers(tpanel);
                        return;
                    }
                }
                this.add_layout(tpanel, this.toolbar_location);
                break;
            }
        }
    };
    Plot.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.properties.toolbar_location.change, function () { return _this._init_toolbar_panel(); });
    };
    Object.defineProperty(Plot.prototype, "plot_canvas", {
        get: function () {
            return this._plot_canvas;
        },
        enumerable: true,
        configurable: true
    });
    Plot.prototype._doc_attached = function () {
        this.plot_canvas.attach_document(this.document); // XXX!
        _super.prototype._doc_attached.call(this);
    };
    Plot.prototype.add_renderers = function () {
        var new_renderers = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            new_renderers[_i] = arguments[_i];
        }
        var renderers = this.renderers;
        renderers = renderers.concat(new_renderers);
        this.renderers = renderers;
    };
    Plot.prototype.add_layout = function (renderer /* XXX: Renderer */, side) {
        if (side === void 0) { side = "center"; }
        if (renderer.props.plot != null)
            renderer.plot = this; // XXX
        if (side != "center") {
            var side_renderers = this.getv(side);
            side_renderers.push(renderer);
            renderer.add_panel(side); // XXX
        }
        this.add_renderers(renderer);
    };
    Plot.prototype.remove_layout = function (renderer) {
        var del = function (items) {
            array_1.removeBy(items, function (item) { return item == renderer; });
        };
        del(this.left);
        del(this.right);
        del(this.above);
        del(this.below);
        del(this.renderers);
    };
    Plot.prototype.add_glyph = function (glyph, source, extra_attrs) {
        if (source === void 0) { source = new column_data_source_1.ColumnDataSource(); }
        if (extra_attrs === void 0) { extra_attrs = {}; }
        var attrs = tslib_1.__assign({}, extra_attrs, { data_source: source, glyph: glyph });
        var renderer = new glyph_renderer_1.GlyphRenderer(attrs);
        this.add_renderers(renderer);
        return renderer;
    };
    Plot.prototype.add_tools = function () {
        var tools = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            tools[_i] = arguments[_i];
        }
        for (var _a = 0, tools_1 = tools; _a < tools_1.length; _a++) {
            var tool = tools_1[_a];
            if (tool.overlay != null) // XXX
                this.add_renderers(tool.overlay);
        }
        this.toolbar.tools = this.toolbar.tools.concat(tools);
    };
    Plot.prototype.get_layoutable_children = function () {
        return [this.plot_canvas];
    };
    Plot.prototype.get_constraints = function () {
        var constraints = _super.prototype.get_constraints.call(this);
        constraints.push(solver_1.EQ(this._width, [-1, this.plot_canvas._width]));
        constraints.push(solver_1.EQ(this._height, [-1, this.plot_canvas._height]));
        return constraints;
    };
    Plot.prototype.get_constrained_variables = function () {
        var vars = tslib_1.__assign({}, _super.prototype.get_constrained_variables.call(this), { on_edge_align_top: this.plot_canvas._top, on_edge_align_bottom: this.plot_canvas._height_minus_bottom, on_edge_align_left: this.plot_canvas._left, on_edge_align_right: this.plot_canvas._width_minus_right, box_cell_align_top: this.plot_canvas._top, box_cell_align_bottom: this.plot_canvas._height_minus_bottom, box_cell_align_left: this.plot_canvas._left, box_cell_align_right: this.plot_canvas._width_minus_right, box_equal_size_top: this.plot_canvas._top, box_equal_size_bottom: this.plot_canvas._height_minus_bottom });
        if (this.sizing_mode != "fixed") {
            vars.box_equal_size_left = this.plot_canvas._left;
            vars.box_equal_size_right = this.plot_canvas._width_minus_right;
        }
        return vars;
    };
    Object.defineProperty(Plot.prototype, "all_renderers", {
        get: function () {
            var renderers = this.renderers;
            for (var _i = 0, _a = this.toolbar.tools; _i < _a.length; _i++) {
                var tool = _a[_i];
                renderers = renderers.concat(tool.synthetic_renderers);
            }
            return renderers;
        },
        enumerable: true,
        configurable: true
    });
    return Plot;
}(layout_dom_1.LayoutDOM));
exports.Plot = Plot;
Plot.initClass();
