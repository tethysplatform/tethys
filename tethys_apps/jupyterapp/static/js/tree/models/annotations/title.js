"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var text_annotation_1 = require("./text_annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
var visuals_1 = require("core/visuals");
var TitleView = /** @class */ (function (_super) {
    tslib_1.__extends(TitleView, _super);
    function TitleView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TitleView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.visuals.text = new visuals_1.Text(this.model);
    };
    TitleView.prototype._get_location = function () {
        var panel = this.model.panel;
        var hmargin = this.model.offset;
        var vmargin = 5;
        var sx, sy;
        switch (panel.side) {
            case 'above':
            case 'below': {
                switch (this.model.vertical_align) {
                    case 'top':
                        sy = panel._top.value + vmargin;
                        break;
                    case 'middle':
                        sy = panel._vcenter.value;
                        break;
                    case 'bottom':
                        sy = panel._bottom.value - vmargin;
                        break;
                    default: throw new Error("unreachable code");
                }
                switch (this.model.align) {
                    case 'left':
                        sx = panel._left.value + hmargin;
                        break;
                    case 'center':
                        sx = panel._hcenter.value;
                        break;
                    case 'right':
                        sx = panel._right.value - hmargin;
                        break;
                    default: throw new Error("unreachable code");
                }
                break;
            }
            case 'left': {
                switch (this.model.vertical_align) {
                    case 'top':
                        sx = panel._left.value - vmargin;
                        break;
                    case 'middle':
                        sx = panel._hcenter.value;
                        break;
                    case 'bottom':
                        sx = panel._right.value + vmargin;
                        break;
                    default: throw new Error("unreachable code");
                }
                switch (this.model.align) {
                    case 'left':
                        sy = panel._bottom.value - hmargin;
                        break;
                    case 'center':
                        sy = panel._vcenter.value;
                        break;
                    case 'right':
                        sy = panel._top.value + hmargin;
                        break;
                    default: throw new Error("unreachable code");
                }
                break;
            }
            case 'right': {
                switch (this.model.vertical_align) {
                    case 'top':
                        sx = panel._right.value - vmargin;
                        break;
                    case 'middle':
                        sx = panel._hcenter.value;
                        break;
                    case 'bottom':
                        sx = panel._left.value + vmargin;
                        break;
                    default: throw new Error("unreachable code");
                }
                switch (this.model.align) {
                    case 'left':
                        sy = panel._top.value + hmargin;
                        break;
                    case 'center':
                        sy = panel._vcenter.value;
                        break;
                    case 'right':
                        sy = panel._bottom.value - hmargin;
                        break;
                    default: throw new Error("unreachable code");
                }
                break;
            }
            default: throw new Error("unreachable code");
        }
        return [sx, sy];
    };
    TitleView.prototype.render = function () {
        if (!this.model.visible) {
            if (this.model.render_mode == 'css')
                dom_1.hide(this.el);
            return;
        }
        var text = this.model.text;
        if (text == null || text.length == 0)
            return;
        this.model.text_baseline = this.model.vertical_align;
        this.model.text_align = this.model.align;
        var _a = this._get_location(), sx = _a[0], sy = _a[1];
        var angle = this.model.panel.get_label_angle_heuristic('parallel');
        var draw = this.model.render_mode == 'canvas' ? this._canvas_text.bind(this) : this._css_text.bind(this);
        draw(this.plot_view.canvas_view.ctx, text, sx, sy, angle);
    };
    TitleView.prototype._get_size = function () {
        var text = this.model.text;
        if (text == null || text.length == 0)
            return 0;
        else {
            var ctx = this.plot_view.canvas_view.ctx;
            this.visuals.text.set_value(ctx);
            return ctx.measureText(text).ascent + 10;
        }
    };
    return TitleView;
}(text_annotation_1.TextAnnotationView));
exports.TitleView = TitleView;
var Title = /** @class */ (function (_super) {
    tslib_1.__extends(Title, _super);
    function Title(attrs) {
        return _super.call(this, attrs) || this;
    }
    Title.initClass = function () {
        this.prototype.type = 'Title';
        this.prototype.default_view = TitleView;
        this.mixins(['line:border_', 'fill:background_']);
        this.define({
            text: [p.String,],
            text_font: [p.Font, 'helvetica'],
            text_font_size: [p.FontSizeSpec, '10pt'],
            text_font_style: [p.FontStyle, 'bold'],
            text_color: [p.ColorSpec, '#444444'],
            text_alpha: [p.NumberSpec, 1.0],
            vertical_align: [p.VerticalAlign, 'bottom'],
            align: [p.TextAlign, 'left'],
            offset: [p.Number, 0],
        });
        this.override({
            background_fill_color: null,
            border_line_color: null,
        });
        this.internal({
            text_align: [p.TextAlign, 'left'],
            text_baseline: [p.TextBaseline, 'bottom'],
        });
    };
    return Title;
}(text_annotation_1.TextAnnotation));
exports.Title = Title;
Title.initClass();
