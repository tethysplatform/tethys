"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var column_data_source_1 = require("../sources/column_data_source");
var p = require("core/properties");
var BandView = /** @class */ (function (_super) {
    tslib_1.__extends(BandView, _super);
    function BandView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BandView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.set_data(this.model.source);
    };
    BandView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.source.streaming, function () { return _this.set_data(_this.model.source); });
        this.connect(this.model.source.patching, function () { return _this.set_data(_this.model.source); });
        this.connect(this.model.source.change, function () { return _this.set_data(_this.model.source); });
    };
    BandView.prototype.set_data = function (source) {
        _super.prototype.set_data.call(this, source);
        this.visuals.warm_cache(source);
        this.plot_view.request_render();
    };
    BandView.prototype._map_data = function () {
        var frame = this.plot_view.frame;
        var dim = this.model.dimension;
        var xscale = frame.xscales[this.model.x_range_name];
        var yscale = frame.yscales[this.model.y_range_name];
        var limit_scale = dim == "height" ? yscale : xscale;
        var base_scale = dim == "height" ? xscale : yscale;
        var limit_view = dim == "height" ? frame.yview : frame.xview;
        var base_view = dim == "height" ? frame.xview : frame.yview;
        var _lower_sx;
        if (this.model.lower.units == "data")
            _lower_sx = limit_scale.v_compute(this._lower);
        else
            _lower_sx = limit_view.v_compute(this._lower);
        var _upper_sx;
        if (this.model.upper.units == "data")
            _upper_sx = limit_scale.v_compute(this._upper);
        else
            _upper_sx = limit_view.v_compute(this._upper);
        var _base_sx;
        if (this.model.base.units == "data")
            _base_sx = base_scale.v_compute(this._base);
        else
            _base_sx = base_view.v_compute(this._base);
        var _a = dim == 'height' ? [1, 0] : [0, 1], i = _a[0], j = _a[1];
        var _lower = [_lower_sx, _base_sx];
        var _upper = [_upper_sx, _base_sx];
        this._lower_sx = _lower[i];
        this._lower_sy = _lower[j];
        this._upper_sx = _upper[i];
        this._upper_sy = _upper[j];
    };
    BandView.prototype.render = function () {
        if (!this.model.visible)
            return;
        this._map_data();
        var ctx = this.plot_view.canvas_view.ctx;
        // Draw the band body
        ctx.beginPath();
        ctx.moveTo(this._lower_sx[0], this._lower_sy[0]);
        for (var i = 0, end = this._lower_sx.length; i < end; i++) {
            ctx.lineTo(this._lower_sx[i], this._lower_sy[i]);
        }
        // iterate backwards so that the upper end is below the lower start
        for (var start = this._upper_sx.length - 1, i = start; i >= 0; i--) {
            ctx.lineTo(this._upper_sx[i], this._upper_sy[i]);
        }
        ctx.closePath();
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_value(ctx);
            ctx.fill();
        }
        // Draw the lower band edge
        ctx.beginPath();
        ctx.moveTo(this._lower_sx[0], this._lower_sy[0]);
        for (var i = 0, end = this._lower_sx.length; i < end; i++) {
            ctx.lineTo(this._lower_sx[i], this._lower_sy[i]);
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_value(ctx);
            ctx.stroke();
        }
        // Draw the upper band edge
        ctx.beginPath();
        ctx.moveTo(this._upper_sx[0], this._upper_sy[0]);
        for (var i = 0, end = this._upper_sx.length; i < end; i++) {
            ctx.lineTo(this._upper_sx[i], this._upper_sy[i]);
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_value(ctx);
            ctx.stroke();
        }
    };
    return BandView;
}(annotation_1.AnnotationView));
exports.BandView = BandView;
var Band = /** @class */ (function (_super) {
    tslib_1.__extends(Band, _super);
    function Band(attrs) {
        return _super.call(this, attrs) || this;
    }
    Band.initClass = function () {
        this.prototype.type = 'Band';
        this.prototype.default_view = BandView;
        this.mixins(['line', 'fill']);
        this.define({
            lower: [p.DistanceSpec],
            upper: [p.DistanceSpec],
            base: [p.DistanceSpec],
            dimension: [p.Dimension, 'height'],
            source: [p.Instance, function () { return new column_data_source_1.ColumnDataSource(); }],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
        this.override({
            fill_color: "#fff9ba",
            fill_alpha: 0.4,
            line_color: "#cccccc",
            line_alpha: 0.3,
        });
    };
    return Band;
}(annotation_1.Annotation));
exports.Band = Band;
Band.initClass();
