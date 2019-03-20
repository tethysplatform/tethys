"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var canvas_1 = require("../canvas/canvas");
var cartesian_frame_1 = require("../canvas/cartesian_frame");
var data_range1d_1 = require("../ranges/data_range1d");
var glyph_renderer_1 = require("../renderers/glyph_renderer");
var layout_dom_1 = require("../layouts/layout_dom");
var bokeh_events_1 = require("core/bokeh_events");
var signaling_1 = require("core/signaling");
var build_views_1 = require("core/build_views");
var ui_events_1 = require("core/ui_events");
var visuals_1 = require("core/visuals");
var dom_view_1 = require("core/dom_view");
var layout_canvas_1 = require("core/layout/layout_canvas");
var alignments_1 = require("core/layout/alignments");
var solver_1 = require("core/layout/solver");
var logging_1 = require("core/logging");
var enums = require("core/enums");
var p = require("core/properties");
var throttle_1 = require("core/util/throttle");
var types_1 = require("core/util/types");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var side_panel_1 = require("core/layout/side_panel");
var global_gl = null;
var PlotCanvasView = /** @class */ (function (_super) {
    tslib_1.__extends(PlotCanvasView, _super);
    function PlotCanvasView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(PlotCanvasView.prototype, "frame", {
        // compat, to be removed
        get: function () {
            return this.model.frame;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(PlotCanvasView.prototype, "canvas", {
        get: function () {
            return this.model.canvas;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(PlotCanvasView.prototype, "canvas_overlays", {
        get: function () {
            return this.canvas_view.overlays_el;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(PlotCanvasView.prototype, "canvas_events", {
        get: function () {
            return this.canvas_view.events_el;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(PlotCanvasView.prototype, "is_paused", {
        get: function () {
            return this._is_paused != null && this._is_paused !== 0;
        },
        enumerable: true,
        configurable: true
    });
    PlotCanvasView.prototype.view_options = function () {
        return { plot_view: this, parent: this };
    };
    PlotCanvasView.prototype.pause = function () {
        if (this._is_paused == null)
            this._is_paused = 1;
        else
            this._is_paused += 1;
    };
    PlotCanvasView.prototype.unpause = function (no_render) {
        if (no_render === void 0) { no_render = false; }
        if (this._is_paused == null)
            throw new Error("wasn't paused");
        this._is_paused -= 1;
        if (this._is_paused == 0 && !no_render)
            this.request_render();
    };
    PlotCanvasView.prototype.request_render = function () {
        this.request_paint();
    };
    PlotCanvasView.prototype.request_paint = function () {
        if (!this.is_paused)
            this.throttled_paint();
    };
    PlotCanvasView.prototype.reset = function () {
        this.clear_state();
        this.reset_range();
        this.reset_selection();
        this.model.plot.trigger_event(new bokeh_events_1.Reset());
    };
    PlotCanvasView.prototype.remove = function () {
        this.ui_event_bus.destroy();
        build_views_1.remove_views(this.renderer_views);
        build_views_1.remove_views(this.tool_views);
        this.canvas_view.remove();
        _super.prototype.remove.call(this);
    };
    PlotCanvasView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-plot-wrapper");
    };
    PlotCanvasView.prototype.initialize = function (options) {
        var _this = this;
        this.pause();
        _super.prototype.initialize.call(this, options);
        this.force_paint = new signaling_1.Signal0(this, "force_paint");
        this.state_changed = new signaling_1.Signal0(this, "state_changed");
        this.lod_started = false;
        this.visuals = new visuals_1.Visuals(this.model.plot); // XXX
        this._initial_state_info = {
            selection: {},
            dimensions: {
                width: this.model.canvas._width.value,
                height: this.model.canvas._height.value,
            },
        };
        this.state = { history: [], index: -1 };
        this.canvas_view = new this.canvas.default_view({ model: this.canvas, parent: this });
        this.el.appendChild(this.canvas_view.el);
        this.canvas_view.render();
        // If requested, try enabling webgl
        if (this.model.plot.output_backend == "webgl")
            this.init_webgl();
        this.throttled_paint = throttle_1.throttle((function () { return _this.force_paint.emit(); }), 15); // TODO (bev) configurable
        this.ui_event_bus = new ui_events_1.UIEvents(this, this.model.toolbar, this.canvas_view.events_el, this.model.plot);
        this.levels = {};
        for (var _i = 0, _a = enums.RenderLevel; _i < _a.length; _i++) {
            var level = _a[_i];
            this.levels[level] = {};
        }
        this.renderer_views = {};
        this.tool_views = {};
        this.build_levels();
        this.build_tools();
        this.update_dataranges();
        this.unpause(true);
        logging_1.logger.debug("PlotView initialized");
    };
    PlotCanvasView.prototype.set_cursor = function (cursor) {
        if (cursor === void 0) { cursor = "default"; }
        this.canvas_view.el.style.cursor = cursor;
    };
    PlotCanvasView.prototype.init_webgl = function () {
        // We use a global invisible canvas and gl context. By having a global context,
        // we avoid the limitation of max 16 contexts that most browsers have.
        if (global_gl == null) {
            var canvas = document.createElement('canvas');
            var opts = { premultipliedAlpha: true };
            var ctx = canvas.getContext("webgl", opts) || canvas.getContext("experimental-webgl", opts);
            // If WebGL is available, we store a reference to the gl canvas on
            // the ctx object, because that's what gets passed everywhere.
            if (ctx != null)
                global_gl = { canvas: canvas, ctx: ctx };
        }
        if (global_gl != null)
            this.gl = global_gl;
        else
            logging_1.logger.warn('WebGL is not supported, falling back to 2D canvas.');
    };
    PlotCanvasView.prototype.prepare_webgl = function (ratio, frame_box) {
        // Prepare WebGL for a drawing pass
        if (this.gl != null) {
            var canvas = this.canvas_view.get_canvas_element();
            // Sync canvas size
            this.gl.canvas.width = canvas.width;
            this.gl.canvas.height = canvas.height;
            // Prepare GL for drawing
            var gl = this.gl.ctx;
            gl.viewport(0, 0, this.gl.canvas.width, this.gl.canvas.height);
            gl.clearColor(0, 0, 0, 0);
            gl.clear(gl.COLOR_BUFFER_BIT || gl.DEPTH_BUFFER_BIT);
            // Clipping
            gl.enable(gl.SCISSOR_TEST);
            var sx = frame_box[0], sy = frame_box[1], w = frame_box[2], h = frame_box[3];
            var _a = this.model.canvas, xview = _a.xview, yview = _a.yview;
            var vx = xview.compute(sx);
            var vy = yview.compute(sy + h);
            gl.scissor(ratio * vx, ratio * vy, ratio * w, ratio * h); // lower left corner, width, height
            // Setup blending
            gl.enable(gl.BLEND);
            gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE_MINUS_DST_ALPHA, gl.ONE); // premultipliedAlpha == true
        }
    };
    //gl.blendFuncSeparate(gl.ONE_MINUS_DST_ALPHA, gl.DST_ALPHA, gl.ONE_MINUS_DST_ALPHA, gl.ONE)  # Without premultipliedAlpha == false
    PlotCanvasView.prototype.blit_webgl = function (ratio) {
        // This should be called when the ctx has no state except the HIDPI transform
        var ctx = this.canvas_view.ctx;
        if (this.gl != null) {
            // Blit gl canvas into the 2D canvas. To do 1-on-1 blitting, we need
            // to remove the hidpi transform, then blit, then restore.
            // ctx.globalCompositeOperation = "source-over"  -> OK; is the default
            logging_1.logger.debug('drawing with WebGL');
            ctx.restore();
            ctx.drawImage(this.gl.canvas, 0, 0);
            // Set back hidpi transform
            ctx.save();
            ctx.scale(ratio, ratio);
            ctx.translate(0.5, 0.5);
        }
    };
    PlotCanvasView.prototype.update_dataranges = function () {
        // Update any DataRange1ds here
        var frame = this.model.frame;
        var bounds = {};
        var log_bounds = {};
        var calculate_log_bounds = false;
        for (var _i = 0, _a = object_1.values(frame.x_ranges).concat(object_1.values(frame.y_ranges)); _i < _a.length; _i++) {
            var r_1 = _a[_i];
            if (r_1 instanceof data_range1d_1.DataRange1d) {
                if (r_1.scale_hint == "log")
                    calculate_log_bounds = true;
            }
        }
        for (var id in this.renderer_views) {
            var view = this.renderer_views[id];
            if (view instanceof glyph_renderer_1.GlyphRendererView) {
                var bds = view.glyph.bounds();
                if (bds != null)
                    bounds[id] = bds;
                if (calculate_log_bounds) {
                    var log_bds = view.glyph.log_bounds();
                    if (log_bds != null)
                        log_bounds[id] = log_bds;
                }
            }
        }
        var follow_enabled = false;
        var has_bounds = false;
        var r;
        if (this.model.plot.match_aspect !== false && this.frame._width.value != 0 && this.frame._height.value != 0)
            r = (1 / this.model.plot.aspect_scale) * (this.frame._width.value / this.frame._height.value);
        for (var _b = 0, _c = object_1.values(frame.x_ranges); _b < _c.length; _b++) {
            var xr = _c[_b];
            if (xr instanceof data_range1d_1.DataRange1d) {
                var bounds_to_use = xr.scale_hint == "log" ? log_bounds : bounds;
                xr.update(bounds_to_use, 0, this.model.id, r);
                if (xr.follow) {
                    follow_enabled = true;
                }
            }
            if (xr.bounds != null)
                has_bounds = true;
        }
        for (var _d = 0, _e = object_1.values(frame.y_ranges); _d < _e.length; _d++) {
            var yr = _e[_d];
            if (yr instanceof data_range1d_1.DataRange1d) {
                var bounds_to_use = yr.scale_hint == "log" ? log_bounds : bounds;
                yr.update(bounds_to_use, 1, this.model.id, r);
                if (yr.follow) {
                    follow_enabled = true;
                }
            }
            if (yr.bounds != null)
                has_bounds = true;
        }
        if (follow_enabled && has_bounds) {
            logging_1.logger.warn('Follow enabled so bounds are unset.');
            for (var _f = 0, _g = object_1.values(frame.x_ranges); _f < _g.length; _f++) {
                var xr = _g[_f];
                xr.bounds = null;
            }
            for (var _h = 0, _j = object_1.values(frame.y_ranges); _h < _j.length; _h++) {
                var yr = _j[_h];
                yr.bounds = null;
            }
        }
        this.range_update_timestamp = Date.now();
    };
    PlotCanvasView.prototype.map_to_screen = function (x, y, x_name, y_name) {
        if (x_name === void 0) { x_name = "default"; }
        if (y_name === void 0) { y_name = "default"; }
        return this.frame.map_to_screen(x, y, x_name, y_name);
    };
    PlotCanvasView.prototype.push_state = function (type, new_info) {
        var _a = this.state, history = _a.history, index = _a.index;
        var prev_info = history[index] != null ? history[index].info : {};
        var info = tslib_1.__assign({}, this._initial_state_info, prev_info, new_info);
        this.state.history = this.state.history.slice(0, this.state.index + 1);
        this.state.history.push({ type: type, info: info });
        this.state.index = this.state.history.length - 1;
        this.state_changed.emit();
    };
    PlotCanvasView.prototype.clear_state = function () {
        this.state = { history: [], index: -1 };
        this.state_changed.emit();
    };
    PlotCanvasView.prototype.can_undo = function () {
        this.state.index >= 0;
    };
    PlotCanvasView.prototype.can_redo = function () {
        this.state.index < this.state.history.length - 1;
    };
    PlotCanvasView.prototype.undo = function () {
        if (this.can_undo()) {
            this.state.index -= 1;
            this._do_state_change(this.state.index);
            this.state_changed.emit();
        }
    };
    PlotCanvasView.prototype.redo = function () {
        if (this.can_redo()) {
            this.state.index += 1;
            this._do_state_change(this.state.index);
            this.state_changed.emit();
        }
    };
    PlotCanvasView.prototype._do_state_change = function (index) {
        var info = this.state.history[index] != null ? this.state.history[index].info : this._initial_state_info;
        if (info.range != null)
            this.update_range(info.range);
        if (info.selection != null)
            this.update_selection(info.selection);
    };
    PlotCanvasView.prototype.get_selection = function () {
        var selection = {};
        for (var _i = 0, _a = this.model.plot.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (renderer instanceof glyph_renderer_1.GlyphRenderer) {
                var selected = renderer.data_source.selected;
                selection[renderer.id] = selected;
            }
        }
        return selection;
    };
    PlotCanvasView.prototype.update_selection = function (selection) {
        for (var _i = 0, _a = this.model.plot.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (!(renderer instanceof glyph_renderer_1.GlyphRenderer))
                continue;
            var ds = renderer.data_source;
            if (selection != null) {
                if (selection[renderer.id] != null)
                    ds.selected = selection[renderer.id];
            }
            else
                ds.selection_manager.clear();
        }
    };
    PlotCanvasView.prototype.reset_selection = function () {
        this.update_selection(null);
    };
    PlotCanvasView.prototype._update_ranges_together = function (range_info_iter) {
        // Get weight needed to scale the diff of the range to honor interval limits
        var weight = 1.0;
        for (var _i = 0, range_info_iter_1 = range_info_iter; _i < range_info_iter_1.length; _i++) {
            var _a = range_info_iter_1[_i], rng = _a[0], range_info = _a[1];
            weight = Math.min(weight, this._get_weight_to_constrain_interval(rng, range_info));
        }
        // Apply shared weight to all ranges
        if (weight < 1) {
            for (var _b = 0, range_info_iter_2 = range_info_iter; _b < range_info_iter_2.length; _b++) {
                var _c = range_info_iter_2[_b], rng = _c[0], range_info = _c[1];
                range_info.start = weight * range_info.start + (1 - weight) * rng.start;
                range_info.end = weight * range_info.end + (1 - weight) * rng.end;
            }
        }
    };
    PlotCanvasView.prototype._update_ranges_individually = function (range_info_iter, is_panning, is_scrolling, maintain_focus) {
        var hit_bound = false;
        for (var _i = 0, range_info_iter_3 = range_info_iter; _i < range_info_iter_3.length; _i++) {
            var _a = range_info_iter_3[_i], rng = _a[0], range_info = _a[1];
            // Limit range interval first. Note that for scroll events,
            // the interval has already been limited for all ranges simultaneously
            if (!is_scrolling) {
                var weight = this._get_weight_to_constrain_interval(rng, range_info);
                if (weight < 1) {
                    range_info.start = weight * range_info.start + (1 - weight) * rng.start;
                    range_info.end = weight * range_info.end + (1 - weight) * rng.end;
                }
            }
            // Prevent range from going outside limits
            // Also ensure that range keeps the same delta when panning/scrolling
            if (rng.bounds != null && rng.bounds != "auto") { // check `auto` for type-checking purpose
                var _b = rng.bounds, min = _b[0], max = _b[1];
                var new_interval = Math.abs(range_info.end - range_info.start);
                if (rng.is_reversed) {
                    if (min != null) {
                        if (min >= range_info.end) {
                            hit_bound = true;
                            range_info.end = min;
                            if (is_panning || is_scrolling) {
                                range_info.start = min + new_interval;
                            }
                        }
                    }
                    if (max != null) {
                        if (max <= range_info.start) {
                            hit_bound = true;
                            range_info.start = max;
                            if (is_panning || is_scrolling) {
                                range_info.end = max - new_interval;
                            }
                        }
                    }
                }
                else {
                    if (min != null) {
                        if (min >= range_info.start) {
                            hit_bound = true;
                            range_info.start = min;
                            if (is_panning || is_scrolling) {
                                range_info.end = min + new_interval;
                            }
                        }
                    }
                    if (max != null) {
                        if (max <= range_info.end) {
                            hit_bound = true;
                            range_info.end = max;
                            if (is_panning || is_scrolling) {
                                range_info.start = max - new_interval;
                            }
                        }
                    }
                }
            }
        }
        // Cancel the event when hitting a bound while scrolling. This ensures that
        // the scroll-zoom tool maintains its focus position. Setting `maintain_focus`
        // to false results in a more "gliding" behavior, allowing one to
        // zoom out more smoothly, at the cost of losing the focus position.
        if (is_scrolling && hit_bound && maintain_focus)
            return;
        for (var _c = 0, range_info_iter_4 = range_info_iter; _c < range_info_iter_4.length; _c++) {
            var _d = range_info_iter_4[_c], rng = _d[0], range_info = _d[1];
            rng.have_updated_interactively = true;
            if (rng.start != range_info.start || rng.end != range_info.end)
                rng.setv(range_info);
        }
    };
    PlotCanvasView.prototype._get_weight_to_constrain_interval = function (rng, range_info) {
        // Get the weight by which a range-update can be applied
        // to still honor the interval limits (including the implicit
        // max interval imposed by the bounds)
        var min_interval = rng.min_interval;
        var max_interval = rng.max_interval;
        // Express bounds as a max_interval. By doing this, the application of
        // bounds and interval limits can be applied independent from each-other.
        if (rng.bounds != null && rng.bounds != "auto") { // check `auto` for type-checking purpose
            var _a = rng.bounds, min = _a[0], max = _a[1];
            if (min != null && max != null) {
                var max_interval2 = Math.abs(max - min);
                max_interval = max_interval != null ? Math.min(max_interval, max_interval2) : max_interval2;
            }
        }
        var weight = 1.0;
        if (min_interval != null || max_interval != null) {
            var old_interval = Math.abs(rng.end - rng.start);
            var new_interval = Math.abs(range_info.end - range_info.start);
            if (min_interval > 0 && new_interval < min_interval) {
                weight = (old_interval - min_interval) / (old_interval - new_interval);
            }
            if (max_interval > 0 && new_interval > max_interval) {
                weight = (max_interval - old_interval) / (new_interval - old_interval);
            }
            weight = Math.max(0.0, Math.min(1.0, weight));
        }
        return weight;
    };
    PlotCanvasView.prototype.update_range = function (range_info, is_panning, is_scrolling, maintain_focus) {
        if (is_panning === void 0) { is_panning = false; }
        if (is_scrolling === void 0) { is_scrolling = false; }
        if (maintain_focus === void 0) { maintain_focus = true; }
        this.pause();
        var _a = this.frame, x_ranges = _a.x_ranges, y_ranges = _a.y_ranges;
        if (range_info == null) {
            for (var name_1 in x_ranges) {
                var rng = x_ranges[name_1];
                rng.reset();
            }
            for (var name_2 in y_ranges) {
                var rng = y_ranges[name_2];
                rng.reset();
            }
            this.update_dataranges();
        }
        else {
            var range_info_iter = [];
            for (var name_3 in x_ranges) {
                var rng = x_ranges[name_3];
                range_info_iter.push([rng, range_info.xrs[name_3]]);
            }
            for (var name_4 in y_ranges) {
                var rng = y_ranges[name_4];
                range_info_iter.push([rng, range_info.yrs[name_4]]);
            }
            if (is_scrolling) {
                this._update_ranges_together(range_info_iter); // apply interval bounds while keeping aspect
            }
            this._update_ranges_individually(range_info_iter, is_panning, is_scrolling, maintain_focus);
        }
        this.unpause();
    };
    PlotCanvasView.prototype.reset_range = function () {
        this.update_range(null);
    };
    PlotCanvasView.prototype.build_levels = function () {
        var renderer_models = this.model.plot.all_renderers;
        // should only bind events on NEW views
        var old_renderers = object_1.keys(this.renderer_views);
        var new_renderer_views = build_views_1.build_views(this.renderer_views, renderer_models, this.view_options());
        var renderers_to_remove = array_1.difference(old_renderers, renderer_models.map(function (model) { return model.id; }));
        for (var level in this.levels) {
            for (var _i = 0, renderers_to_remove_1 = renderers_to_remove; _i < renderers_to_remove_1.length; _i++) {
                var id = renderers_to_remove_1[_i];
                delete this.levels[level][id];
            }
        }
        for (var _a = 0, new_renderer_views_1 = new_renderer_views; _a < new_renderer_views_1.length; _a++) {
            var view = new_renderer_views_1[_a];
            this.levels[view.model.level][view.model.id] = view;
        }
    };
    PlotCanvasView.prototype.get_renderer_views = function () {
        var _this = this;
        return this.model.plot.renderers.map(function (r) { return _this.levels[r.level][r.id]; });
    };
    PlotCanvasView.prototype.build_tools = function () {
        var _this = this;
        var tool_models = this.model.plot.toolbar.tools;
        var new_tool_views = build_views_1.build_views(this.tool_views, tool_models, this.view_options());
        new_tool_views.map(function (tool_view) { return _this.ui_event_bus.register_tool(tool_view); });
    };
    PlotCanvasView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.force_paint, function () { return _this.repaint(); });
        var _a = this.model.frame, x_ranges = _a.x_ranges, y_ranges = _a.y_ranges;
        for (var name_5 in x_ranges) {
            var rng = x_ranges[name_5];
            this.connect(rng.change, function () { return _this.request_render(); });
        }
        for (var name_6 in y_ranges) {
            var rng = y_ranges[name_6];
            this.connect(rng.change, function () { return _this.request_render(); });
        }
        this.connect(this.model.plot.properties.renderers.change, function () { return _this.build_levels(); });
        this.connect(this.model.plot.toolbar.properties.tools.change, function () { _this.build_levels(); _this.build_tools(); });
        this.connect(this.model.plot.change, function () { return _this.request_render(); });
        this.connect(this.model.plot.reset, function () { return _this.reset(); });
    };
    PlotCanvasView.prototype.set_initial_range = function () {
        // check for good values for ranges before setting initial range
        var good_vals = true;
        var _a = this.frame, x_ranges = _a.x_ranges, y_ranges = _a.y_ranges;
        var xrs = {};
        var yrs = {};
        for (var name_7 in x_ranges) {
            var _b = x_ranges[name_7], start = _b.start, end = _b.end;
            if (start == null || end == null || types_1.isStrictNaN(start + end)) {
                good_vals = false;
                break;
            }
            xrs[name_7] = { start: start, end: end };
        }
        if (good_vals) {
            for (var name_8 in y_ranges) {
                var _c = y_ranges[name_8], start = _c.start, end = _c.end;
                if (start == null || end == null || types_1.isStrictNaN(start + end)) {
                    good_vals = false;
                    break;
                }
                yrs[name_8] = { start: start, end: end };
            }
        }
        if (good_vals) {
            this._initial_state_info.range = { xrs: xrs, yrs: yrs };
            logging_1.logger.debug("initial ranges set");
        }
        else
            logging_1.logger.warn('could not set initial ranges');
    };
    PlotCanvasView.prototype.update_constraints = function () {
        this.solver.suggest_value(this.frame._width, this.canvas._width.value);
        this.solver.suggest_value(this.frame._height, this.canvas._height.value);
        for (var id in this.renderer_views) {
            var view = this.renderer_views[id];
            if (side_panel_1.isSizeableView(view) && view.model.panel != null)
                side_panel_1.update_panel_constraints(view);
        }
        this.solver.update_variables();
    };
    // XXX: bacause PlotCanvas is NOT a LayoutDOM
    PlotCanvasView.prototype._layout = function (final) {
        if (final === void 0) { final = false; }
        this.render();
        if (final) {
            this.model.plot.setv({
                inner_width: Math.round(this.frame._width.value),
                inner_height: Math.round(this.frame._height.value),
                layout_width: Math.round(this.canvas._width.value),
                layout_height: Math.round(this.canvas._height.value),
            }, { no_change: true });
            // XXX: can't be @request_paint(), because it would trigger back-and-forth
            // layout recomputing feedback loop between plots. Plots are also much more
            // responsive this way, especially in interactive mode.
            this.paint();
        }
    };
    PlotCanvasView.prototype.has_finished = function () {
        if (!_super.prototype.has_finished.call(this)) {
            return false;
        }
        for (var level in this.levels) {
            var renderer_views = this.levels[level];
            for (var id in renderer_views) {
                var view = renderer_views[id];
                if (!view.has_finished())
                    return false;
            }
        }
        return true;
    };
    PlotCanvasView.prototype.render = function () {
        // Set the plot and canvas to the current model's size
        // This gets called upon solver resize events
        var width = this.model._width.value;
        var height = this.model._height.value;
        this.canvas_view.set_dims([width, height]);
        this.update_constraints();
        if (this.model.plot.match_aspect !== false && this.frame._width.value != 0 && this.frame._height.value != 0)
            this.update_dataranges();
        // This allows the plot canvas to be positioned around the toolbar
        this.el.style.position = 'absolute';
        this.el.style.left = this.model._dom_left.value + "px";
        this.el.style.top = this.model._dom_top.value + "px";
        this.el.style.width = this.model._width.value + "px";
        this.el.style.height = this.model._height.value + "px";
    };
    PlotCanvasView.prototype._needs_layout = function () {
        for (var id in this.renderer_views) {
            var view = this.renderer_views[id];
            if (side_panel_1.isSizeableView(view) && view.model.panel != null) {
                if (side_panel_1._view_sizes.get(view) != view.get_size())
                    return true;
            }
        }
        return false;
    };
    PlotCanvasView.prototype.repaint = function () {
        if (this._needs_layout())
            this.parent.partial_layout(); // XXX
        else
            this.paint();
    };
    PlotCanvasView.prototype.paint = function () {
        var _this = this;
        if (this.is_paused)
            return;
        logging_1.logger.trace("PlotCanvas.render() for " + this.model.id);
        // Prepare the canvas size, taking HIDPI into account. Note that this may cause a resize
        // of the canvas, which means that any previous calls to ctx.save() will be undone.
        this.canvas_view.prepare_canvas();
        var document = this.model.document;
        if (document != null) {
            var interactive_duration = document.interactive_duration();
            var plot_1 = this.model.plot;
            if (interactive_duration >= 0 && interactive_duration < plot_1.lod_interval) {
                setTimeout(function () {
                    if (document.interactive_duration() > plot_1.lod_timeout) {
                        document.interactive_stop(plot_1);
                    }
                    _this.request_render();
                }, plot_1.lod_timeout);
            }
            else
                document.interactive_stop(plot_1);
        }
        for (var id in this.renderer_views) {
            var v = this.renderer_views[id];
            if (this.range_update_timestamp == null ||
                (v instanceof glyph_renderer_1.GlyphRendererView && v.set_data_timestamp > this.range_update_timestamp)) {
                this.update_dataranges();
                break;
            }
        }
        // TODO (bev) OK this sucks, but the event from the solver update doesn't
        // reach the frame in time (sometimes) so force an update here for now
        // (mp) not only that, but models don't know about solver anymore, so
        // frame can't update its scales.
        this.model.frame.update_scales();
        var ctx = this.canvas_view.ctx;
        var ratio = this.canvas.pixel_ratio;
        // Set hidpi-transform
        ctx.save(); // Save default state, do *after* getting ratio, cause setting canvas.width resets transforms
        ctx.scale(ratio, ratio);
        ctx.translate(0.5, 0.5);
        var frame_box = [
            this.frame._left.value,
            this.frame._top.value,
            this.frame._width.value,
            this.frame._height.value,
        ];
        this._map_hook(ctx, frame_box);
        this._paint_empty(ctx, frame_box);
        this.prepare_webgl(ratio, frame_box);
        ctx.save();
        if (this.visuals.outline_line.doit) {
            this.visuals.outline_line.set_value(ctx);
            var x0 = frame_box[0], y0 = frame_box[1], w = frame_box[2], h = frame_box[3];
            // XXX: shrink outline region by 1px to make right and bottom lines visible
            // if they are on the edge of the canvas.
            if (x0 + w == this.canvas._width.value) {
                w -= 1;
            }
            if (y0 + h == this.canvas._height.value) {
                h -= 1;
            }
            ctx.strokeRect(x0, y0, w, h);
        }
        ctx.restore();
        this._paint_levels(ctx, ['image', 'underlay', 'glyph'], frame_box, true);
        this.blit_webgl(ratio);
        this._paint_levels(ctx, ['annotation'], frame_box, true);
        this._paint_levels(ctx, ['overlay'], frame_box, false);
        if (this._initial_state_info.range == null)
            this.set_initial_range();
        ctx.restore(); // Restore to default state
        if (!this._has_finished) {
            this._has_finished = true;
            this.notify_finished();
        }
    };
    PlotCanvasView.prototype._paint_levels = function (ctx, levels, clip_region, global_clip) {
        ctx.save();
        if (global_clip) {
            ctx.beginPath();
            ctx.rect.apply(ctx, clip_region);
            ctx.clip();
        }
        var indices = {};
        for (var i = 0; i < this.model.plot.renderers.length; i++) {
            var renderer = this.model.plot.renderers[i];
            indices[renderer.id] = i;
        }
        var sortKey = function (renderer_view) { return indices[renderer_view.model.id]; };
        for (var _i = 0, levels_1 = levels; _i < levels_1.length; _i++) {
            var level = levels_1[_i];
            var renderer_views = array_1.sortBy(object_1.values(this.levels[level]), sortKey);
            for (var _a = 0, renderer_views_1 = renderer_views; _a < renderer_views_1.length; _a++) {
                var renderer_view = renderer_views_1[_a];
                if (!global_clip && renderer_view.needs_clip) {
                    ctx.save();
                    ctx.beginPath();
                    ctx.rect.apply(ctx, clip_region);
                    ctx.clip();
                }
                renderer_view.render();
                if (!global_clip && renderer_view.needs_clip) {
                    ctx.restore();
                }
            }
        }
        ctx.restore();
    };
    PlotCanvasView.prototype._map_hook = function (_ctx, _frame_box) { };
    PlotCanvasView.prototype._paint_empty = function (ctx, frame_box) {
        var _a = [0, 0, this.canvas_view.model._width.value, this.canvas_view.model._height.value], cx = _a[0], cy = _a[1], cw = _a[2], ch = _a[3];
        var fx = frame_box[0], fy = frame_box[1], fw = frame_box[2], fh = frame_box[3];
        ctx.clearRect(cx, cy, cw, ch);
        if (this.visuals.border_fill.doit) {
            this.visuals.border_fill.set_value(ctx);
            ctx.fillRect(cx, cy, cw, ch);
            ctx.clearRect(fx, fy, fw, fh);
        }
        if (this.visuals.background_fill.doit) {
            this.visuals.background_fill.set_value(ctx);
            ctx.fillRect(fx, fy, fw, fh);
        }
    };
    PlotCanvasView.prototype.save = function (name) {
        switch (this.model.plot.output_backend) {
            case "canvas":
            case "webgl": {
                var canvas = this.canvas_view.get_canvas_element();
                if (canvas.msToBlob != null) {
                    var blob = canvas.msToBlob();
                    window.navigator.msSaveBlob(blob, name);
                }
                else {
                    var link = document.createElement('a');
                    link.href = canvas.toDataURL('image/png');
                    link.download = name + ".png";
                    link.target = "_blank";
                    link.dispatchEvent(new MouseEvent('click'));
                }
                break;
            }
            case "svg": {
                var ctx = this.canvas_view._ctx;
                var svg = ctx.getSerializedSvg(true);
                var svgblob = new Blob([svg], { type: 'text/plain' });
                var downloadLink = document.createElement("a");
                downloadLink.download = name + ".svg";
                downloadLink.innerHTML = "Download svg";
                downloadLink.href = window.URL.createObjectURL(svgblob);
                downloadLink.onclick = function (event) { return document.body.removeChild(event.target); };
                downloadLink.style.display = "none";
                document.body.appendChild(downloadLink);
                downloadLink.click();
                break;
            }
        }
    };
    return PlotCanvasView;
}(dom_view_1.DOMView));
exports.PlotCanvasView = PlotCanvasView;
var AbovePanel = /** @class */ (function (_super) {
    tslib_1.__extends(AbovePanel, _super);
    function AbovePanel() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AbovePanel.initClass = function () {
        this.prototype.type = "AbovePanel";
    };
    return AbovePanel;
}(layout_canvas_1.LayoutCanvas));
exports.AbovePanel = AbovePanel;
AbovePanel.initClass();
var BelowPanel = /** @class */ (function (_super) {
    tslib_1.__extends(BelowPanel, _super);
    function BelowPanel() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BelowPanel.initClass = function () {
        this.prototype.type = "BelowPanel";
    };
    return BelowPanel;
}(layout_canvas_1.LayoutCanvas));
exports.BelowPanel = BelowPanel;
BelowPanel.initClass();
var LeftPanel = /** @class */ (function (_super) {
    tslib_1.__extends(LeftPanel, _super);
    function LeftPanel() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LeftPanel.initClass = function () {
        this.prototype.type = "LeftPanel";
    };
    return LeftPanel;
}(layout_canvas_1.LayoutCanvas));
exports.LeftPanel = LeftPanel;
LeftPanel.initClass();
var RightPanel = /** @class */ (function (_super) {
    tslib_1.__extends(RightPanel, _super);
    function RightPanel() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RightPanel.initClass = function () {
        this.prototype.type = "RightPanel";
    };
    return RightPanel;
}(layout_canvas_1.LayoutCanvas));
exports.RightPanel = RightPanel;
RightPanel.initClass();
var PlotCanvas = /** @class */ (function (_super) {
    tslib_1.__extends(PlotCanvas, _super);
    function PlotCanvas(attrs) {
        return _super.call(this, attrs) || this;
    }
    PlotCanvas.initClass = function () {
        this.prototype.type = 'PlotCanvas';
        this.prototype.default_view = PlotCanvasView;
        this.internal({
            plot: [p.Instance],
            toolbar: [p.Instance],
            canvas: [p.Instance],
            frame: [p.Instance],
        });
        this.override({
            // We should find a way to enforce this
            sizing_mode: 'stretch_both',
        });
    };
    PlotCanvas.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.canvas = new canvas_1.Canvas({
            map: this.use_map != null ? this.use_map : false,
            use_hidpi: this.plot.hidpi,
            output_backend: this.plot.output_backend,
        });
        this.frame = new cartesian_frame_1.CartesianFrame({
            x_range: this.plot.x_range,
            extra_x_ranges: this.plot.extra_x_ranges,
            x_scale: this.plot.x_scale,
            y_range: this.plot.y_range,
            extra_y_ranges: this.plot.extra_y_ranges,
            y_scale: this.plot.y_scale,
        });
        this.above_panel = new AbovePanel();
        this.below_panel = new BelowPanel();
        this.left_panel = new LeftPanel();
        this.right_panel = new RightPanel();
        logging_1.logger.debug("PlotCanvas initialized");
    };
    PlotCanvas.prototype._doc_attached = function () {
        this.canvas.attach_document(this.document);
        this.frame.attach_document(this.document);
        this.above_panel.attach_document(this.document);
        this.below_panel.attach_document(this.document);
        this.left_panel.attach_document(this.document);
        this.right_panel.attach_document(this.document);
        _super.prototype._doc_attached.call(this);
        logging_1.logger.debug("PlotCanvas attached to document");
    };
    PlotCanvas.prototype.get_layoutable_children = function () {
        var children = [
            this.above_panel, this.below_panel,
            this.left_panel, this.right_panel,
            this.canvas, this.frame,
        ];
        var collect_panels = function (layout_renderers) {
            for (var _i = 0, layout_renderers_1 = layout_renderers; _i < layout_renderers_1.length; _i++) {
                var r = layout_renderers_1[_i];
                if (side_panel_1.isSizeable(r) && r.panel != null)
                    children.push(r.panel);
            }
        };
        collect_panels(this.plot.above);
        collect_panels(this.plot.below);
        collect_panels(this.plot.left);
        collect_panels(this.plot.right);
        return children; // XXX: PlotCanvas should be a LayoutCanvas
    };
    PlotCanvas.prototype.get_constraints = function () {
        return _super.prototype.get_constraints.call(this).concat(this._get_constant_constraints(), this._get_side_constraints());
    };
    PlotCanvas.prototype._get_constant_constraints = function () {
        return [
            // Set the origin. Everything else is positioned absolutely wrt canvas.
            solver_1.EQ(this.canvas._left, 0),
            solver_1.EQ(this.canvas._top, 0),
            solver_1.GE(this.above_panel._top, [-1, this.canvas._top]),
            solver_1.EQ(this.above_panel._bottom, [-1, this.frame._top]),
            solver_1.EQ(this.above_panel._left, [-1, this.left_panel._right]),
            solver_1.EQ(this.above_panel._right, [-1, this.right_panel._left]),
            solver_1.EQ(this.below_panel._top, [-1, this.frame._bottom]),
            solver_1.LE(this.below_panel._bottom, [-1, this.canvas._bottom]),
            solver_1.EQ(this.below_panel._left, [-1, this.left_panel._right]),
            solver_1.EQ(this.below_panel._right, [-1, this.right_panel._left]),
            solver_1.EQ(this.left_panel._top, [-1, this.above_panel._bottom]),
            solver_1.EQ(this.left_panel._bottom, [-1, this.below_panel._top]),
            solver_1.GE(this.left_panel._left, [-1, this.canvas._left]),
            solver_1.EQ(this.left_panel._right, [-1, this.frame._left]),
            solver_1.EQ(this.right_panel._top, [-1, this.above_panel._bottom]),
            solver_1.EQ(this.right_panel._bottom, [-1, this.below_panel._top]),
            solver_1.EQ(this.right_panel._left, [-1, this.frame._right]),
            solver_1.LE(this.right_panel._right, [-1, this.canvas._right]),
            solver_1.EQ(this._top, [-1, this.above_panel._bottom]),
            solver_1.EQ(this._left, [-1, this.left_panel._right]),
            solver_1.EQ(this._height, [-1, this._bottom], [-1, this.canvas._bottom], this.below_panel._top),
            solver_1.EQ(this._width, [-1, this._right], [-1, this.canvas._right], this.right_panel._left),
            solver_1.GE(this._top, -this.plot.min_border_top),
            solver_1.GE(this._left, -this.plot.min_border_left),
            solver_1.GE(this._height, [-1, this._bottom], -this.plot.min_border_bottom),
            solver_1.GE(this._width, [-1, this._right], -this.plot.min_border_right),
        ];
    };
    PlotCanvas.prototype._get_side_constraints = function () {
        var panels = function (objs) { return objs.map(function (obj) { return obj.panel; }); };
        var above = alignments_1.vstack(this.above_panel, panels(this.plot.above));
        var below = alignments_1.vstack(this.below_panel, array_1.reversed(panels(this.plot.below)));
        var left = alignments_1.hstack(this.left_panel, panels(this.plot.left));
        var right = alignments_1.hstack(this.right_panel, array_1.reversed(panels(this.plot.right)));
        return array_1.concat([above, below, left, right]);
    };
    return PlotCanvas;
}(layout_dom_1.LayoutDOM));
exports.PlotCanvas = PlotCanvas;
PlotCanvas.initClass();
