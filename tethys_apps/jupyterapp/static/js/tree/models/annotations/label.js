"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var text_annotation_1 = require("./text_annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
var LabelView = /** @class */ (function (_super) {
    tslib_1.__extends(LabelView, _super);
    function LabelView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LabelView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.visuals.warm_cache();
    };
    LabelView.prototype._get_size = function () {
        var ctx = this.plot_view.canvas_view.ctx;
        this.visuals.text.set_value(ctx);
        if (this.model.panel.is_horizontal) {
            var height = ctx.measureText(this.model.text).ascent;
            return height;
        }
        else {
            var width = ctx.measureText(this.model.text).width;
            return width;
        }
    };
    LabelView.prototype.render = function () {
        if (!this.model.visible && this.model.render_mode == 'css')
            dom_1.hide(this.el);
        if (!this.model.visible)
            return;
        // Here because AngleSpec does units tranform and label doesn't support specs
        var angle;
        switch (this.model.angle_units) {
            case "rad": {
                angle = -this.model.angle;
                break;
            }
            case "deg": {
                angle = (-this.model.angle * Math.PI) / 180.0;
                break;
            }
            default:
                throw new Error("unreachable code");
        }
        var panel = this.model.panel != null ? this.model.panel : this.plot_view.frame;
        var xscale = this.plot_view.frame.xscales[this.model.x_range_name];
        var yscale = this.plot_view.frame.yscales[this.model.y_range_name];
        var sx = this.model.x_units == "data" ? xscale.compute(this.model.x) : panel.xview.compute(this.model.x);
        var sy = this.model.y_units == "data" ? yscale.compute(this.model.y) : panel.yview.compute(this.model.y);
        sx += this.model.x_offset;
        sy -= this.model.y_offset;
        var draw = this.model.render_mode == 'canvas' ? this._canvas_text.bind(this) : this._css_text.bind(this);
        draw(this.plot_view.canvas_view.ctx, this.model.text, sx, sy, angle);
    };
    return LabelView;
}(text_annotation_1.TextAnnotationView));
exports.LabelView = LabelView;
var Label = /** @class */ (function (_super) {
    tslib_1.__extends(Label, _super);
    function Label(attrs) {
        return _super.call(this, attrs) || this;
    }
    Label.initClass = function () {
        this.prototype.type = 'Label';
        this.prototype.default_view = LabelView;
        this.mixins(['text', 'line:border_', 'fill:background_']);
        this.define({
            x: [p.Number,],
            x_units: [p.SpatialUnits, 'data'],
            y: [p.Number,],
            y_units: [p.SpatialUnits, 'data'],
            text: [p.String,],
            angle: [p.Angle, 0],
            angle_units: [p.AngleUnits, 'rad'],
            x_offset: [p.Number, 0],
            y_offset: [p.Number, 0],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
        this.override({
            background_fill_color: null,
            border_line_color: null,
        });
    };
    return Label;
}(text_annotation_1.TextAnnotation));
exports.Label = Label;
Label.initClass();
