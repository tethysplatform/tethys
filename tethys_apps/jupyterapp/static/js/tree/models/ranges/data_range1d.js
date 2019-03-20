"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var data_range_1 = require("./data_range");
var glyph_renderer_1 = require("../renderers/glyph_renderer");
var logging_1 = require("core/logging");
var p = require("core/properties");
var bbox = require("core/util/bbox");
var array_1 = require("core/util/array");
var DataRange1d = /** @class */ (function (_super) {
    tslib_1.__extends(DataRange1d, _super);
    function DataRange1d(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this._plot_bounds = {};
        _this.have_updated_interactively = false;
        return _this;
    }
    DataRange1d.initClass = function () {
        this.prototype.type = "DataRange1d";
        this.define({
            start: [p.Number],
            end: [p.Number],
            range_padding: [p.Number, 0.1],
            range_padding_units: [p.PaddingUnits, "percent"],
            flipped: [p.Bool, false],
            follow: [p.StartEnd,],
            follow_interval: [p.Number],
            default_span: [p.Number, 2],
        });
        this.internal({
            scale_hint: [p.String, 'auto'],
        });
    };
    DataRange1d.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._initial_start = this.start;
        this._initial_end = this.end;
        this._initial_range_padding = this.range_padding;
        this._initial_range_padding_units = this.range_padding_units;
        this._initial_follow = this.follow;
        this._initial_follow_interval = this.follow_interval;
        this._initial_default_span = this.default_span;
    };
    Object.defineProperty(DataRange1d.prototype, "min", {
        get: function () {
            return Math.min(this.start, this.end);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(DataRange1d.prototype, "max", {
        get: function () {
            return Math.max(this.start, this.end);
        },
        enumerable: true,
        configurable: true
    });
    DataRange1d.prototype.computed_renderers = function () {
        // TODO (bev) check that renderers actually configured with this range
        var names = this.names;
        var renderers = this.renderers;
        if (renderers.length == 0) {
            for (var _i = 0, _a = this.plots; _i < _a.length; _i++) {
                var plot = _a[_i];
                var rs = plot.renderers.filter(function (r) { return r instanceof glyph_renderer_1.GlyphRenderer; });
                renderers = renderers.concat(rs);
            }
        }
        if (names.length > 0)
            renderers = renderers.filter(function (r) { return array_1.includes(names, r.name); });
        logging_1.logger.debug("computed " + renderers.length + " renderers for DataRange1d " + this.id);
        for (var _b = 0, renderers_1 = renderers; _b < renderers_1.length; _b++) {
            var r = renderers_1[_b];
            logging_1.logger.trace(" - " + r.type + " " + r.id);
        }
        return renderers;
    };
    DataRange1d.prototype._compute_plot_bounds = function (renderers, bounds) {
        var result = bbox.empty();
        for (var _i = 0, renderers_2 = renderers; _i < renderers_2.length; _i++) {
            var r = renderers_2[_i];
            if (bounds[r.id] != null)
                result = bbox.union(result, bounds[r.id]);
        }
        return result;
    };
    DataRange1d.prototype.adjust_bounds_for_aspect = function (bounds, ratio) {
        var result = bbox.empty();
        var width = bounds.maxX - bounds.minX;
        if (width <= 0) {
            width = 1.0;
        }
        var height = bounds.maxY - bounds.minY;
        if (height <= 0) {
            height = 1.0;
        }
        var xcenter = 0.5 * (bounds.maxX + bounds.minX);
        var ycenter = 0.5 * (bounds.maxY + bounds.minY);
        if (width < ratio * height) {
            width = ratio * height;
        }
        else {
            height = width / ratio;
        }
        result.maxX = xcenter + 0.5 * width;
        result.minX = xcenter - 0.5 * width;
        result.maxY = ycenter + 0.5 * height;
        result.minY = ycenter - 0.5 * height;
        return result;
    };
    DataRange1d.prototype._compute_min_max = function (plot_bounds, dimension) {
        var _a, _b;
        var overall = bbox.empty();
        for (var k in plot_bounds) {
            var v = plot_bounds[k];
            overall = bbox.union(overall, v);
        }
        var min, max;
        if (dimension == 0)
            _a = [overall.minX, overall.maxX], min = _a[0], max = _a[1];
        else
            _b = [overall.minY, overall.maxY], min = _b[0], max = _b[1];
        return [min, max];
    };
    DataRange1d.prototype._compute_range = function (min, max) {
        var _a;
        var range_padding = this.range_padding; // XXX: ? 0
        var start, end;
        if (this.scale_hint == "log") {
            if (isNaN(min) || !isFinite(min) || min <= 0) {
                if (isNaN(max) || !isFinite(max) || max <= 0)
                    min = 0.1;
                else
                    min = max / 100;
                logging_1.logger.warn("could not determine minimum data value for log axis, DataRange1d using value " + min);
            }
            if (isNaN(max) || !isFinite(max) || max <= 0) {
                if (isNaN(min) || !isFinite(min) || min <= 0)
                    max = 10;
                else
                    max = min * 100;
                logging_1.logger.warn("could not determine maximum data value for log axis, DataRange1d using value " + max);
            }
            var center = void 0, span = void 0;
            if (max == min) {
                span = this.default_span + 0.001;
                center = Math.log(min) / Math.log(10);
            }
            else {
                var log_min = void 0, log_max = void 0;
                if (this.range_padding_units == "percent") {
                    log_min = Math.log(min) / Math.log(10);
                    log_max = Math.log(max) / Math.log(10);
                    span = (log_max - log_min) * (1 + range_padding);
                }
                else {
                    log_min = Math.log(min - range_padding) / Math.log(10);
                    log_max = Math.log(max + range_padding) / Math.log(10);
                    span = log_max - log_min;
                }
                center = (log_min + log_max) / 2.0;
            }
            start = Math.pow(10, center - span / 2.0);
            end = Math.pow(10, center + span / 2.0);
        }
        else {
            var span = void 0;
            if (max == min)
                span = this.default_span;
            else {
                if (this.range_padding_units == "percent")
                    span = (max - min) * (1 + range_padding);
                else
                    span = (max - min) + 2 * range_padding;
            }
            var center = (max + min) / 2.0;
            start = center - span / 2.0;
            end = center + span / 2.0;
        }
        var follow_sign = +1;
        if (this.flipped) {
            _a = [end, start], start = _a[0], end = _a[1];
            follow_sign = -1;
        }
        var follow_interval = this.follow_interval;
        if (follow_interval != null && Math.abs(start - end) > follow_interval) {
            if (this.follow == 'start')
                end = start + follow_sign * follow_interval;
            else if (this.follow == 'end')
                start = end - follow_sign * follow_interval;
        }
        return [start, end];
    };
    DataRange1d.prototype.update = function (bounds, dimension, bounds_id, ratio) {
        if (this.have_updated_interactively)
            return;
        var renderers = this.computed_renderers();
        // update the raw data bounds for all renderers we care about
        var total_bounds = this._compute_plot_bounds(renderers, bounds);
        if (ratio != null)
            total_bounds = this.adjust_bounds_for_aspect(total_bounds, ratio);
        this._plot_bounds[bounds_id] = total_bounds;
        // compute the min/mix for our specified dimension
        var _a = this._compute_min_max(this._plot_bounds, dimension), min = _a[0], max = _a[1];
        // derive start, end from bounds and data range config
        var _b = this._compute_range(min, max), start = _b[0], end = _b[1];
        if (this._initial_start != null) {
            if (this.scale_hint == "log") {
                if (this._initial_start > 0)
                    start = this._initial_start;
            }
            else
                start = this._initial_start;
        }
        if (this._initial_end != null) {
            if (this.scale_hint == "log") {
                if (this._initial_end > 0)
                    end = this._initial_end;
            }
            else
                end = this._initial_end;
        }
        // only trigger updates when there are changes
        var _c = [this.start, this.end], _start = _c[0], _end = _c[1];
        if (start != _start || end != _end) {
            var new_range = {};
            if (start != _start)
                new_range.start = start;
            if (end != _end)
                new_range.end = end;
            this.setv(new_range);
        }
        if (this.bounds == 'auto')
            this.setv({ bounds: [start, end] }, { silent: true });
        this.change.emit();
    };
    DataRange1d.prototype.reset = function () {
        this.have_updated_interactively = false;
        // change events silenced as PlotCanvasView.update_dataranges triggers property callbacks
        this.setv({
            range_padding: this._initial_range_padding,
            range_padding_units: this._initial_range_padding_units,
            follow: this._initial_follow,
            follow_interval: this._initial_follow_interval,
            default_span: this._initial_default_span,
        }, { silent: true });
        this.change.emit();
    };
    return DataRange1d;
}(data_range_1.DataRange));
exports.DataRange1d = DataRange1d;
DataRange1d.initClass();
