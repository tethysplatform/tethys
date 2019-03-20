"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var p = require("core/properties");
var SlopeView = /** @class */ (function (_super) {
    tslib_1.__extends(SlopeView, _super);
    function SlopeView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SlopeView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
    };
    SlopeView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
    };
    SlopeView.prototype.render = function () {
        if (!this.model.visible)
            return;
        this._draw_slope();
    };
    SlopeView.prototype._draw_slope = function () {
        var gradient = this.model.gradient;
        var y_intercept = this.model.y_intercept;
        if (gradient == null || y_intercept == null) {
            return;
        }
        var frame = this.plot_view.frame;
        var xscale = frame.xscales[this.model.x_range_name];
        var yscale = frame.yscales[this.model.y_range_name];
        var sy_start = frame._top.value;
        var sy_end = sy_start + frame._height.value;
        var y_start = yscale.invert(sy_start);
        var y_end = yscale.invert(sy_end);
        var x_start = (y_start - y_intercept) / gradient;
        var x_end = (y_end - y_intercept) / gradient;
        var sx_start = xscale.compute(x_start);
        var sx_end = xscale.compute(x_end);
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        ctx.beginPath();
        this.visuals.line.set_value(ctx);
        ctx.moveTo(sx_start, sy_start);
        ctx.lineTo(sx_end, sy_end);
        ctx.stroke();
        ctx.restore();
    };
    return SlopeView;
}(annotation_1.AnnotationView));
exports.SlopeView = SlopeView;
var Slope = /** @class */ (function (_super) {
    tslib_1.__extends(Slope, _super);
    function Slope(attrs) {
        return _super.call(this, attrs) || this;
    }
    Slope.initClass = function () {
        this.prototype.type = 'Slope';
        this.prototype.default_view = SlopeView;
        this.mixins(['line']);
        this.define({
            gradient: [p.Number, null],
            y_intercept: [p.Number, null],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
        this.override({
            line_color: 'black',
        });
    };
    return Slope;
}(annotation_1.Annotation));
exports.Slope = Slope;
Slope.initClass();
