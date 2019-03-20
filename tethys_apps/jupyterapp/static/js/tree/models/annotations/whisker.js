"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var column_data_source_1 = require("../sources/column_data_source");
var arrow_head_1 = require("./arrow_head");
var p = require("core/properties");
var WhiskerView = /** @class */ (function (_super) {
    tslib_1.__extends(WhiskerView, _super);
    function WhiskerView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WhiskerView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.set_data(this.model.source);
    };
    WhiskerView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.source.streaming, function () { return _this.set_data(_this.model.source); });
        this.connect(this.model.source.patching, function () { return _this.set_data(_this.model.source); });
        this.connect(this.model.source.change, function () { return _this.set_data(_this.model.source); });
    };
    WhiskerView.prototype.set_data = function (source) {
        _super.prototype.set_data.call(this, source);
        this.visuals.warm_cache(source);
        this.plot_view.request_render();
    };
    WhiskerView.prototype._map_data = function () {
        var frame = this.plot_model.frame;
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
    WhiskerView.prototype.render = function () {
        if (!this.model.visible)
            return;
        this._map_data();
        var ctx = this.plot_view.canvas_view.ctx;
        if (this.visuals.line.doit) {
            for (var i = 0, end = this._lower_sx.length; i < end; i++) {
                this.visuals.line.set_vectorize(ctx, i);
                ctx.beginPath();
                ctx.moveTo(this._lower_sx[i], this._lower_sy[i]);
                ctx.lineTo(this._upper_sx[i], this._upper_sy[i]);
                ctx.stroke();
            }
        }
        var angle = this.model.dimension == "height" ? 0 : Math.PI / 2;
        if (this.model.lower_head != null) {
            for (var i = 0, end = this._lower_sx.length; i < end; i++) {
                ctx.save();
                ctx.translate(this._lower_sx[i], this._lower_sy[i]);
                ctx.rotate(angle + Math.PI);
                this.model.lower_head.render(ctx, i);
                ctx.restore();
            }
        }
        if (this.model.upper_head != null) {
            for (var i = 0, end = this._upper_sx.length; i < end; i++) {
                ctx.save();
                ctx.translate(this._upper_sx[i], this._upper_sy[i]);
                ctx.rotate(angle);
                this.model.upper_head.render(ctx, i);
                ctx.restore();
            }
        }
    };
    return WhiskerView;
}(annotation_1.AnnotationView));
exports.WhiskerView = WhiskerView;
var Whisker = /** @class */ (function (_super) {
    tslib_1.__extends(Whisker, _super);
    function Whisker(attrs) {
        return _super.call(this, attrs) || this;
    }
    Whisker.initClass = function () {
        this.prototype.type = 'Whisker';
        this.prototype.default_view = WhiskerView;
        this.mixins(['line']);
        this.define({
            lower: [p.DistanceSpec],
            lower_head: [p.Instance, function () { return new arrow_head_1.TeeHead({ level: "underlay", size: 10 }); }],
            upper: [p.DistanceSpec],
            upper_head: [p.Instance, function () { return new arrow_head_1.TeeHead({ level: "underlay", size: 10 }); }],
            base: [p.DistanceSpec],
            dimension: [p.Dimension, 'height'],
            source: [p.Instance, function () { return new column_data_source_1.ColumnDataSource(); }],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
        this.override({
            level: 'underlay',
        });
    };
    return Whisker;
}(annotation_1.Annotation));
exports.Whisker = Whisker;
Whisker.initClass();
