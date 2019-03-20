"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var signaling_1 = require("core/signaling");
var p = require("core/properties");
var PolyAnnotationView = /** @class */ (function (_super) {
    tslib_1.__extends(PolyAnnotationView, _super);
    function PolyAnnotationView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PolyAnnotationView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        // need to respond to either normal BB change events or silent
        // "data only updates" that tools might want to use
        this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
        this.connect(this.model.data_update, function () { return _this.plot_view.request_render(); });
    };
    PolyAnnotationView.prototype.render = function () {
        if (!this.model.visible)
            return;
        var _a = this.model, xs = _a.xs, ys = _a.ys;
        if (xs.length != ys.length)
            return;
        if (xs.length < 3 || ys.length < 3)
            return;
        var frame = this.plot_view.frame;
        var ctx = this.plot_view.canvas_view.ctx;
        for (var i = 0, end = xs.length; i < end; i++) {
            var sx = void 0;
            if (this.model.xs_units == 'screen')
                sx = this.model.screen ? xs[i] : frame.xview.compute(xs[i]);
            else
                throw new Error("not implemented");
            var sy = void 0;
            if (this.model.ys_units == 'screen')
                sy = this.model.screen ? ys[i] : frame.yview.compute(ys[i]);
            else
                throw new Error("not implemented");
            if (i == 0) {
                ctx.beginPath();
                ctx.moveTo(sx, sy);
            }
            else {
                ctx.lineTo(sx, sy);
            }
        }
        ctx.closePath();
        if (this.visuals.line.doit) {
            this.visuals.line.set_value(ctx);
            ctx.stroke();
        }
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_value(ctx);
            ctx.fill();
        }
    };
    return PolyAnnotationView;
}(annotation_1.AnnotationView));
exports.PolyAnnotationView = PolyAnnotationView;
var PolyAnnotation = /** @class */ (function (_super) {
    tslib_1.__extends(PolyAnnotation, _super);
    function PolyAnnotation(attrs) {
        return _super.call(this, attrs) || this;
    }
    PolyAnnotation.initClass = function () {
        this.prototype.type = "PolyAnnotation";
        this.prototype.default_view = PolyAnnotationView;
        this.mixins(['line', 'fill']);
        this.define({
            xs: [p.Array, []],
            xs_units: [p.SpatialUnits, 'data'],
            ys: [p.Array, []],
            ys_units: [p.SpatialUnits, 'data'],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
        this.internal({
            screen: [p.Boolean, false],
        });
        this.override({
            fill_color: "#fff9ba",
            fill_alpha: 0.4,
            line_color: "#cccccc",
            line_alpha: 0.3,
        });
    };
    PolyAnnotation.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.data_update = new signaling_1.Signal0(this, "data_update");
    };
    PolyAnnotation.prototype.update = function (_a) {
        var xs = _a.xs, ys = _a.ys;
        this.setv({ xs: xs, ys: ys, screen: true }, { silent: true });
        this.data_update.emit();
    };
    return PolyAnnotation;
}(annotation_1.Annotation));
exports.PolyAnnotation = PolyAnnotation;
PolyAnnotation.initClass();
