"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
var SpanView = /** @class */ (function (_super) {
    tslib_1.__extends(SpanView, _super);
    function SpanView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SpanView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.plot_view.canvas_overlays.appendChild(this.el);
        this.el.style.position = "absolute";
        dom_1.hide(this.el);
    };
    SpanView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        if (this.model.for_hover)
            this.connect(this.model.properties.computed_location.change, function () { return _this._draw_span(); });
        else {
            if (this.model.render_mode == 'canvas') {
                this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
                this.connect(this.model.properties.location.change, function () { return _this.plot_view.request_render(); });
            }
            else {
                this.connect(this.model.change, function () { return _this.render(); });
                this.connect(this.model.properties.location.change, function () { return _this._draw_span(); });
            }
        }
    };
    SpanView.prototype.render = function () {
        if (!this.model.visible && this.model.render_mode == 'css')
            dom_1.hide(this.el);
        if (!this.model.visible)
            return;
        this._draw_span();
    };
    SpanView.prototype._draw_span = function () {
        var _this = this;
        var loc = this.model.for_hover ? this.model.computed_location : this.model.location;
        if (loc == null) {
            dom_1.hide(this.el);
            return;
        }
        var frame = this.plot_view.frame;
        var xscale = frame.xscales[this.model.x_range_name];
        var yscale = frame.yscales[this.model.y_range_name];
        var _calc_dim = function (scale, view) {
            if (_this.model.for_hover)
                return _this.model.computed_location;
            else {
                if (_this.model.location_units == 'data')
                    return scale.compute(loc);
                else
                    return view.compute(loc);
            }
        };
        var height, sleft, stop, width;
        if (this.model.dimension == 'width') {
            stop = _calc_dim(yscale, frame.yview);
            sleft = frame._left.value;
            width = frame._width.value;
            height = this.model.properties.line_width.value();
        }
        else {
            stop = frame._top.value;
            sleft = _calc_dim(xscale, frame.xview);
            width = this.model.properties.line_width.value();
            height = frame._height.value;
        }
        if (this.model.render_mode == "css") {
            this.el.style.top = stop + "px";
            this.el.style.left = sleft + "px";
            this.el.style.width = width + "px";
            this.el.style.height = height + "px";
            this.el.style.backgroundColor = this.model.properties.line_color.value();
            this.el.style.opacity = this.model.properties.line_alpha.value();
            dom_1.show(this.el);
        }
        else if (this.model.render_mode == "canvas") {
            var ctx = this.plot_view.canvas_view.ctx;
            ctx.save();
            ctx.beginPath();
            this.visuals.line.set_value(ctx);
            ctx.moveTo(sleft, stop);
            if (this.model.dimension == "width") {
                ctx.lineTo(sleft + width, stop);
            }
            else {
                ctx.lineTo(sleft, stop + height);
            }
            ctx.stroke();
            ctx.restore();
        }
    };
    return SpanView;
}(annotation_1.AnnotationView));
exports.SpanView = SpanView;
var Span = /** @class */ (function (_super) {
    tslib_1.__extends(Span, _super);
    function Span(attrs) {
        return _super.call(this, attrs) || this;
    }
    Span.initClass = function () {
        this.prototype.type = 'Span';
        this.prototype.default_view = SpanView;
        this.mixins(['line']);
        this.define({
            render_mode: [p.RenderMode, 'canvas'],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
            location: [p.Number, null],
            location_units: [p.SpatialUnits, 'data'],
            dimension: [p.Dimension, 'width'],
        });
        this.override({
            line_color: 'black',
        });
        this.internal({
            for_hover: [p.Boolean, false],
            computed_location: [p.Number, null],
        });
    };
    return Span;
}(annotation_1.Annotation));
exports.Span = Span;
Span.initClass();
