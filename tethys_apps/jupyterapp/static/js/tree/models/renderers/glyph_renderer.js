"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var renderer_1 = require("./renderer");
var line_1 = require("../glyphs/line");
var cds_view_1 = require("../sources/cds_view");
var logging_1 = require("core/logging");
var p = require("core/properties");
var arrayable_1 = require("core/util/arrayable");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var factor_range_1 = require("../ranges/factor_range");
var selection_defaults = {
    fill: {},
    line: {},
};
var decimated_defaults = {
    fill: { fill_alpha: 0.3, fill_color: "grey" },
    line: { line_alpha: 0.3, line_color: "grey" },
};
var nonselection_defaults = {
    fill: { fill_alpha: 0.2 },
    line: {},
};
var GlyphRendererView = /** @class */ (function (_super) {
    tslib_1.__extends(GlyphRendererView, _super);
    function GlyphRendererView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    GlyphRendererView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        var base_glyph = this.model.glyph;
        var has_fill = array_1.includes(base_glyph.mixins, "fill");
        var has_line = array_1.includes(base_glyph.mixins, "line");
        var glyph_attrs = object_1.clone(base_glyph.attributes);
        delete glyph_attrs.id;
        function mk_glyph(defaults) {
            var attrs = object_1.clone(glyph_attrs);
            if (has_fill)
                object_1.extend(attrs, defaults.fill);
            if (has_line)
                object_1.extend(attrs, defaults.line);
            return new base_glyph.constructor(attrs);
        }
        this.glyph = this.build_glyph_view(base_glyph);
        var selection_glyph = this.model.selection_glyph;
        if (selection_glyph == null)
            selection_glyph = mk_glyph({ fill: {}, line: {} });
        else if (selection_glyph === "auto")
            selection_glyph = mk_glyph(selection_defaults);
        this.selection_glyph = this.build_glyph_view(selection_glyph);
        var nonselection_glyph = this.model.nonselection_glyph;
        if ((nonselection_glyph == null))
            nonselection_glyph = mk_glyph({ fill: {}, line: {} });
        else if (nonselection_glyph === "auto")
            nonselection_glyph = mk_glyph(nonselection_defaults);
        this.nonselection_glyph = this.build_glyph_view(nonselection_glyph);
        var hover_glyph = this.model.hover_glyph;
        if (hover_glyph != null)
            this.hover_glyph = this.build_glyph_view(hover_glyph);
        var muted_glyph = this.model.muted_glyph;
        if (muted_glyph != null)
            this.muted_glyph = this.build_glyph_view(muted_glyph);
        var decimated_glyph = mk_glyph(decimated_defaults);
        this.decimated_glyph = this.build_glyph_view(decimated_glyph);
        this.xscale = this.plot_view.frame.xscales[this.model.x_range_name];
        this.yscale = this.plot_view.frame.yscales[this.model.y_range_name];
        this.set_data(false);
    };
    GlyphRendererView.prototype.build_glyph_view = function (model) {
        return new model.default_view({ model: model, renderer: this, plot_view: this.plot_view, parent: this }); // XXX
    };
    GlyphRendererView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.request_render(); });
        this.connect(this.model.glyph.change, function () { return _this.set_data(); });
        this.connect(this.model.data_source.change, function () { return _this.set_data(); });
        this.connect(this.model.data_source.streaming, function () { return _this.set_data(); });
        this.connect(this.model.data_source.patching, function (indices /* XXX: WHY? */) { return _this.set_data(true, indices); });
        this.connect(this.model.data_source.selected.change, function () { return _this.request_render(); });
        this.connect(this.model.data_source._select, function () { return _this.request_render(); });
        if (this.hover_glyph != null)
            this.connect(this.model.data_source.inspect, function () { return _this.request_render(); });
        this.connect(this.model.properties.view.change, function () { return _this.set_data(); });
        this.connect(this.model.view.change, function () { return _this.set_data(); });
        var _a = this.plot_model.frame, x_ranges = _a.x_ranges, y_ranges = _a.y_ranges;
        for (var name_1 in x_ranges) {
            var rng = x_ranges[name_1];
            if (rng instanceof factor_range_1.FactorRange)
                this.connect(rng.change, function () { return _this.set_data(); });
        }
        for (var name_2 in y_ranges) {
            var rng = y_ranges[name_2];
            if (rng instanceof factor_range_1.FactorRange)
                this.connect(rng.change, function () { return _this.set_data(); });
        }
        this.connect(this.model.glyph.transformchange, function () { return _this.set_data(); });
    };
    GlyphRendererView.prototype.have_selection_glyphs = function () {
        return this.selection_glyph != null && this.nonselection_glyph != null;
    };
    // in case of partial updates like patching, the list of indices that actually
    // changed may be passed as the "indices" parameter to afford any optional optimizations
    GlyphRendererView.prototype.set_data = function (request_render, indices) {
        if (request_render === void 0) { request_render = true; }
        if (indices === void 0) { indices = null; }
        var t0 = Date.now();
        var source = this.model.data_source;
        this.all_indices = this.model.view.indices;
        // TODO (bev) this is a bit clunky, need to make sure glyphs use the correct ranges when they call
        // mapping functions on the base Renderer class
        this.glyph.model.setv({ x_range_name: this.model.x_range_name,
            y_range_name: this.model.y_range_name }, { silent: true });
        this.glyph.set_data(source, this.all_indices, indices);
        this.glyph.set_visuals(source);
        this.decimated_glyph.set_visuals(source);
        if (this.have_selection_glyphs()) {
            this.selection_glyph.set_visuals(source);
            this.nonselection_glyph.set_visuals(source);
        }
        if (this.hover_glyph != null)
            this.hover_glyph.set_visuals(source);
        if (this.muted_glyph != null)
            this.muted_glyph.set_visuals(source);
        var lod_factor = this.plot_model.plot.lod_factor;
        this.decimated = [];
        for (var i = 0, end = Math.floor(this.all_indices.length / lod_factor); i < end; i++) {
            this.decimated.push(i * lod_factor);
        }
        var dt = Date.now() - t0;
        logging_1.logger.debug(this.glyph.model.type + " GlyphRenderer (" + this.model.id + "): set_data finished in " + dt + "ms");
        this.set_data_timestamp = Date.now();
        if (request_render)
            this.request_render();
    };
    GlyphRendererView.prototype.render = function () {
        var _this = this;
        if (!this.model.visible)
            return;
        var t0 = Date.now();
        var glsupport = this.glyph.glglyph;
        this.glyph.map_data();
        var dtmap = Date.now() - t0;
        var tmask = Date.now();
        // all_indices is in full data space, indices is converted to subset space
        // either by mask_data (that uses the spatial index) or manually
        var indices = this.glyph.mask_data(this.all_indices);
        if (indices.length === this.all_indices.length) {
            indices = array_1.range(0, this.all_indices.length);
        }
        var dtmask = Date.now() - tmask;
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        // selected is in full set space
        var selected = this.model.data_source.selected;
        var selected_full_indices;
        if (!selected || selected.is_empty()) {
            selected_full_indices = [];
        }
        else {
            if (this.glyph instanceof line_1.LineView && selected.selected_glyph === this.glyph.model) {
                selected_full_indices = this.model.view.convert_indices_from_subset(indices);
            }
            else {
                selected_full_indices = selected.indices;
            }
        }
        // inspected is in full set space
        var inspected = this.model.data_source.inspected;
        var inspected_full_indices;
        if (!inspected || (inspected.length === 0)) {
            inspected_full_indices = [];
        }
        else {
            if (inspected['0d'].glyph) {
                inspected_full_indices = this.model.view.convert_indices_from_subset(indices);
            }
            else if (inspected['1d'].indices.length > 0) {
                inspected_full_indices = inspected['1d'].indices;
            }
            else {
                inspected_full_indices = ((function () {
                    var result = [];
                    for (var _i = 0, _a = Object.keys(inspected["2d"].indices); _i < _a.length; _i++) {
                        var i = _a[_i];
                        result.push(parseInt(i));
                    }
                    return result;
                })());
            }
        }
        // inspected is transformed to subset space
        var inspected_subset_indices = ((function () {
            var result = [];
            for (var _i = 0, indices_2 = indices; _i < indices_2.length; _i++) {
                var i = indices_2[_i];
                if (array_1.includes(inspected_full_indices, _this.all_indices[i]))
                    result.push(i);
            }
            return result;
        })());
        var lod_threshold = this.plot_model.plot.lod_threshold;
        var glyph;
        var nonselection_glyph;
        var selection_glyph;
        if ((this.model.document != null ? this.model.document.interactive_duration() > 0 : false)
            && !glsupport && lod_threshold != null && this.all_indices.length > lod_threshold) {
            // Render decimated during interaction if too many elements and not using GL
            indices = this.decimated;
            glyph = this.decimated_glyph;
            nonselection_glyph = this.decimated_glyph;
            selection_glyph = this.selection_glyph;
        }
        else {
            glyph = this.model.muted && this.muted_glyph != null ? this.muted_glyph : this.glyph;
            nonselection_glyph = this.nonselection_glyph;
            selection_glyph = this.selection_glyph;
        }
        if (this.hover_glyph != null && inspected_subset_indices.length)
            indices = array_1.difference(indices, inspected_subset_indices);
        // Render with no selection
        var dtselect = null;
        var trender;
        if (!(selected_full_indices.length && this.have_selection_glyphs())) {
            trender = Date.now();
            if (this.glyph instanceof line_1.LineView) {
                if (this.hover_glyph && inspected_subset_indices.length)
                    this.hover_glyph.render(ctx, this.model.view.convert_indices_from_subset(inspected_subset_indices), this.glyph);
                else
                    glyph.render(ctx, this.all_indices, this.glyph);
            }
            else {
                glyph.render(ctx, indices, this.glyph);
                if (this.hover_glyph && inspected_subset_indices.length)
                    this.hover_glyph.render(ctx, inspected_subset_indices, this.glyph);
            }
            // Render with selection
        }
        else {
            // reset the selection mask
            var tselect = Date.now();
            var selected_mask = {};
            for (var _i = 0, selected_full_indices_1 = selected_full_indices; _i < selected_full_indices_1.length; _i++) {
                var i = selected_full_indices_1[_i];
                selected_mask[i] = true;
            }
            // intersect/different selection with render mask
            var selected_subset_indices = new Array();
            var nonselected_subset_indices = new Array();
            // now, selected is changed to subset space, except for Line glyph
            if (this.glyph instanceof line_1.LineView) {
                for (var _a = 0, _b = this.all_indices; _a < _b.length; _a++) {
                    var i = _b[_a];
                    if (selected_mask[i] != null)
                        selected_subset_indices.push(i);
                    else
                        nonselected_subset_indices.push(i);
                }
            }
            else {
                for (var _c = 0, indices_1 = indices; _c < indices_1.length; _c++) {
                    var i = indices_1[_c];
                    if (selected_mask[this.all_indices[i]] != null)
                        selected_subset_indices.push(i);
                    else
                        nonselected_subset_indices.push(i);
                }
            }
            dtselect = Date.now() - tselect;
            trender = Date.now();
            nonselection_glyph.render(ctx, nonselected_subset_indices, this.glyph);
            selection_glyph.render(ctx, selected_subset_indices, this.glyph);
            if (this.hover_glyph != null) {
                if (this.glyph instanceof line_1.LineView)
                    this.hover_glyph.render(ctx, this.model.view.convert_indices_from_subset(inspected_subset_indices), this.glyph);
                else
                    this.hover_glyph.render(ctx, inspected_subset_indices, this.glyph);
            }
        }
        var dtrender = Date.now() - trender;
        this.last_dtrender = dtrender;
        var dttot = Date.now() - t0;
        logging_1.logger.debug(this.glyph.model.type + " GlyphRenderer (" + this.model.id + "): render finished in " + dttot + "ms");
        logging_1.logger.trace(" - map_data finished in       : " + dtmap + "ms");
        logging_1.logger.trace(" - mask_data finished in      : " + dtmask + "ms");
        if (dtselect != null) {
            logging_1.logger.trace(" - selection mask finished in : " + dtselect + "ms");
        }
        logging_1.logger.trace(" - glyph renders finished in  : " + dtrender + "ms");
        return ctx.restore();
    };
    GlyphRendererView.prototype.draw_legend = function (ctx, x0, x1, y0, y1, field, label, index) {
        if (index == null)
            index = this.model.get_reference_point(field, label);
        this.glyph.draw_legend_for_index(ctx, { x0: x0, x1: x1, y0: y0, y1: y1 }, index);
    };
    GlyphRendererView.prototype.hit_test = function (geometry) {
        if (!this.model.visible)
            return null;
        var hit_test_result = this.glyph.hit_test(geometry);
        // glyphs that don't have hit-testing implemented will return null
        if (hit_test_result == null)
            return null;
        return this.model.view.convert_selection_from_subset(hit_test_result);
    };
    return GlyphRendererView;
}(renderer_1.RendererView));
exports.GlyphRendererView = GlyphRendererView;
var GlyphRenderer = /** @class */ (function (_super) {
    tslib_1.__extends(GlyphRenderer, _super);
    function GlyphRenderer(attrs) {
        return _super.call(this, attrs) || this;
    }
    GlyphRenderer.initClass = function () {
        this.prototype.type = 'GlyphRenderer';
        this.prototype.default_view = GlyphRendererView;
        this.define({
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
            data_source: [p.Instance],
            view: [p.Instance, function () { return new cds_view_1.CDSView(); }],
            glyph: [p.Instance],
            hover_glyph: [p.Instance],
            nonselection_glyph: [p.Any, 'auto'],
            selection_glyph: [p.Any, 'auto'],
            muted_glyph: [p.Instance],
            muted: [p.Bool, false],
        });
        this.override({
            level: 'glyph',
        });
    };
    GlyphRenderer.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        if (this.view.source == null) {
            this.view.source = this.data_source;
            this.view.compute_indices();
        }
    };
    GlyphRenderer.prototype.get_reference_point = function (field, value) {
        var index = 0;
        if (field != null) {
            var data = this.data_source.get_column(field);
            if (data != null) {
                var i = arrayable_1.indexOf(data, value);
                if (i != -1)
                    index = i;
            }
        }
        return index;
    };
    GlyphRenderer.prototype.get_selection_manager = function () {
        return this.data_source.selection_manager;
    };
    return GlyphRenderer;
}(renderer_1.Renderer));
exports.GlyphRenderer = GlyphRenderer;
GlyphRenderer.initClass();
