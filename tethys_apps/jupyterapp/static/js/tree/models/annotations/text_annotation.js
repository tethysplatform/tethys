"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
var text_1 = require("core/util/text");
var TextAnnotationView = /** @class */ (function (_super) {
    tslib_1.__extends(TextAnnotationView, _super);
    function TextAnnotationView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TextAnnotationView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        if (this.model.render_mode == 'css') {
            this.el.classList.add('bk-annotation');
            this.plot_view.canvas_overlays.appendChild(this.el);
        }
    };
    TextAnnotationView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        if (this.model.render_mode == 'css') {
            // dispatch CSS update immediately
            this.connect(this.model.change, function () { return _this.render(); });
        }
        else {
            this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
        }
    };
    TextAnnotationView.prototype._calculate_text_dimensions = function (ctx, text) {
        var width = ctx.measureText(text).width;
        var height = text_1.get_text_height(this.visuals.text.font_value()).height;
        return [width, height];
    };
    TextAnnotationView.prototype._calculate_bounding_box_dimensions = function (ctx, text) {
        var _a = this._calculate_text_dimensions(ctx, text), width = _a[0], height = _a[1];
        var x_offset;
        switch (ctx.textAlign) {
            case 'left':
                x_offset = 0;
                break;
            case 'center':
                x_offset = -width / 2;
                break;
            case 'right':
                x_offset = -width;
                break;
            default:
                throw new Error("unreachable code");
        }
        // guestimated from https://www.w3.org/TR/2dcontext/#dom-context-2d-textbaseline
        var y_offset;
        switch (ctx.textBaseline) {
            case 'top':
                y_offset = 0.0;
                break;
            case 'middle':
                y_offset = -0.5 * height;
                break;
            case 'bottom':
                y_offset = -1.0 * height;
                break;
            case 'alphabetic':
                y_offset = -0.8 * height;
                break;
            case 'hanging':
                y_offset = -0.17 * height;
                break;
            case 'ideographic':
                y_offset = -0.83 * height;
                break;
            default:
                throw new Error("unreachable code");
        }
        return [x_offset, y_offset, width, height];
    };
    TextAnnotationView.prototype._canvas_text = function (ctx, text, sx, sy, angle) {
        this.visuals.text.set_value(ctx);
        var bbox_dims = this._calculate_bounding_box_dimensions(ctx, text);
        ctx.save();
        ctx.beginPath();
        ctx.translate(sx, sy);
        if (angle)
            ctx.rotate(angle);
        ctx.rect(bbox_dims[0], bbox_dims[1], bbox_dims[2], bbox_dims[3]);
        if (this.visuals.background_fill.doit) {
            this.visuals.background_fill.set_value(ctx);
            ctx.fill();
        }
        if (this.visuals.border_line.doit) {
            this.visuals.border_line.set_value(ctx);
            ctx.stroke();
        }
        if (this.visuals.text.doit) {
            this.visuals.text.set_value(ctx);
            ctx.fillText(text, 0, 0);
        }
        ctx.restore();
    };
    TextAnnotationView.prototype._css_text = function (ctx, text, sx, sy, angle) {
        dom_1.hide(this.el);
        this.visuals.text.set_value(ctx);
        var bbox_dims = this._calculate_bounding_box_dimensions(ctx, text);
        // attempt to support vector string-style ("8 4 8") line dashing for css mode
        var ld = this.visuals.border_line.line_dash.value();
        var line_dash = ld.length < 2 ? "solid" : "dashed";
        this.visuals.border_line.set_value(ctx);
        this.visuals.background_fill.set_value(ctx);
        this.el.style.position = 'absolute';
        this.el.style.left = sx + bbox_dims[0] + "px";
        this.el.style.top = sy + bbox_dims[1] + "px";
        this.el.style.color = "" + this.visuals.text.text_color.value();
        this.el.style.opacity = "" + this.visuals.text.text_alpha.value();
        this.el.style.font = "" + this.visuals.text.font_value();
        this.el.style.lineHeight = "normal"; // needed to prevent ipynb css override
        if (angle) {
            this.el.style.transform = "rotate(" + angle + "rad)";
        }
        if (this.visuals.background_fill.doit) {
            this.el.style.backgroundColor = "" + this.visuals.background_fill.color_value();
        }
        if (this.visuals.border_line.doit) {
            this.el.style.borderStyle = "" + line_dash;
            this.el.style.borderWidth = this.visuals.border_line.line_width.value() + "px";
            this.el.style.borderColor = "" + this.visuals.border_line.color_value();
        }
        this.el.textContent = text;
        dom_1.show(this.el);
    };
    return TextAnnotationView;
}(annotation_1.AnnotationView));
exports.TextAnnotationView = TextAnnotationView;
var TextAnnotation = /** @class */ (function (_super) {
    tslib_1.__extends(TextAnnotation, _super);
    function TextAnnotation(attrs) {
        return _super.call(this, attrs) || this;
    }
    TextAnnotation.initClass = function () {
        this.prototype.type = "TextAnnotation";
        this.define({
            render_mode: [p.RenderMode, "canvas"],
        });
    };
    return TextAnnotation;
}(annotation_1.Annotation));
exports.TextAnnotation = TextAnnotation;
TextAnnotation.initClass();
