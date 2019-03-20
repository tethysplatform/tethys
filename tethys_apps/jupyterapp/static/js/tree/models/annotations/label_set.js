"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var text_annotation_1 = require("./text_annotation");
var column_data_source_1 = require("../sources/column_data_source");
var dom_1 = require("core/dom");
var p = require("core/properties");
var LabelSetView = /** @class */ (function (_super) {
    tslib_1.__extends(LabelSetView, _super);
    function LabelSetView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LabelSetView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.set_data(this.model.source);
        if (this.model.render_mode == 'css') {
            for (var i = 0, end = this._text.length; i < end; i++) {
                var el = dom_1.div({ class: 'bk-annotation-child', style: { display: "none" } });
                this.el.appendChild(el);
            }
        }
    };
    LabelSetView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        if (this.model.render_mode == 'css') {
            // dispatch CSS update immediately
            this.connect(this.model.change, function () {
                _this.set_data(_this.model.source);
                _this.render();
            });
            this.connect(this.model.source.streaming, function () {
                _this.set_data(_this.model.source);
                _this.render();
            });
            this.connect(this.model.source.patching, function () {
                _this.set_data(_this.model.source);
                _this.render();
            });
            this.connect(this.model.source.change, function () {
                _this.set_data(_this.model.source);
                _this.render();
            });
        }
        else {
            this.connect(this.model.change, function () {
                _this.set_data(_this.model.source);
                _this.plot_view.request_render();
            });
            this.connect(this.model.source.streaming, function () {
                _this.set_data(_this.model.source);
                _this.plot_view.request_render();
            });
            this.connect(this.model.source.patching, function () {
                _this.set_data(_this.model.source);
                _this.plot_view.request_render();
            });
            this.connect(this.model.source.change, function () {
                _this.set_data(_this.model.source);
                _this.plot_view.request_render();
            });
        }
    };
    LabelSetView.prototype.set_data = function (source) {
        _super.prototype.set_data.call(this, source);
        this.visuals.warm_cache(source);
    };
    LabelSetView.prototype._map_data = function () {
        var xscale = this.plot_view.frame.xscales[this.model.x_range_name];
        var yscale = this.plot_view.frame.yscales[this.model.y_range_name];
        var panel = this.model.panel != null ? this.model.panel : this.plot_view.frame;
        var sx = this.model.x_units == "data" ? xscale.v_compute(this._x) : panel.xview.v_compute(this._x);
        var sy = this.model.y_units == "data" ? yscale.v_compute(this._y) : panel.yview.v_compute(this._y);
        return [sx, sy];
    };
    LabelSetView.prototype.render = function () {
        if (!this.model.visible && this.model.render_mode == 'css')
            dom_1.hide(this.el);
        if (!this.model.visible)
            return;
        var draw = this.model.render_mode == 'canvas' ? this._v_canvas_text.bind(this) : this._v_css_text.bind(this);
        var ctx = this.plot_view.canvas_view.ctx;
        var _a = this._map_data(), sx = _a[0], sy = _a[1];
        for (var i = 0, end = this._text.length; i < end; i++) {
            draw(ctx, i, this._text[i], sx[i] + this._x_offset[i], sy[i] - this._y_offset[i], this._angle[i]);
        }
    };
    LabelSetView.prototype._get_size = function () {
        var ctx = this.plot_view.canvas_view.ctx;
        this.visuals.text.set_value(ctx);
        switch (this.model.panel.side) {
            case "above":
            case "below": {
                var height = ctx.measureText(this._text[0]).ascent;
                return height;
            }
            case "left":
            case "right": {
                var width = ctx.measureText(this._text[0]).width;
                return width;
            }
            default:
                throw new Error("unreachable code");
        }
    };
    LabelSetView.prototype._v_canvas_text = function (ctx, i, text, sx, sy, angle) {
        this.visuals.text.set_vectorize(ctx, i);
        var bbox_dims = this._calculate_bounding_box_dimensions(ctx, text);
        ctx.save();
        ctx.beginPath();
        ctx.translate(sx, sy);
        ctx.rotate(angle);
        ctx.rect(bbox_dims[0], bbox_dims[1], bbox_dims[2], bbox_dims[3]);
        if (this.visuals.background_fill.doit) {
            this.visuals.background_fill.set_vectorize(ctx, i);
            ctx.fill();
        }
        if (this.visuals.border_line.doit) {
            this.visuals.border_line.set_vectorize(ctx, i);
            ctx.stroke();
        }
        if (this.visuals.text.doit) {
            this.visuals.text.set_vectorize(ctx, i);
            ctx.fillText(text, 0, 0);
        }
        ctx.restore();
    };
    LabelSetView.prototype._v_css_text = function (ctx, i, text, sx, sy, angle) {
        var el = this.el.children[i];
        el.textContent = text;
        this.visuals.text.set_vectorize(ctx, i);
        var bbox_dims = this._calculate_bounding_box_dimensions(ctx, text);
        // attempt to support vector-style ("8 4 8") line dashing for css mode
        var ld = this.visuals.border_line.line_dash.value();
        var line_dash = ld.length < 2 ? "solid" : "dashed";
        this.visuals.border_line.set_vectorize(ctx, i);
        this.visuals.background_fill.set_vectorize(ctx, i);
        el.style.position = 'absolute';
        el.style.left = sx + bbox_dims[0] + "px";
        el.style.top = sy + bbox_dims[1] + "px";
        el.style.color = "" + this.visuals.text.text_color.value();
        el.style.opacity = "" + this.visuals.text.text_alpha.value();
        el.style.font = "" + this.visuals.text.font_value();
        el.style.lineHeight = "normal"; // needed to prevent ipynb css override
        if (angle) {
            el.style.transform = "rotate(" + angle + "rad)";
        }
        if (this.visuals.background_fill.doit) {
            el.style.backgroundColor = "" + this.visuals.background_fill.color_value();
        }
        if (this.visuals.border_line.doit) {
            el.style.borderStyle = "" + line_dash;
            el.style.borderWidth = this.visuals.border_line.line_width.value() + "px";
            el.style.borderColor = "" + this.visuals.border_line.color_value();
        }
        dom_1.show(el);
    };
    return LabelSetView;
}(text_annotation_1.TextAnnotationView));
exports.LabelSetView = LabelSetView;
var LabelSet = /** @class */ (function (_super) {
    tslib_1.__extends(LabelSet, _super);
    function LabelSet(attrs) {
        return _super.call(this, attrs) || this;
    }
    LabelSet.initClass = function () {
        this.prototype.type = 'LabelSet';
        this.prototype.default_view = LabelSetView;
        this.mixins(['text', 'line:border_', 'fill:background_']);
        this.define({
            x: [p.NumberSpec],
            y: [p.NumberSpec],
            x_units: [p.SpatialUnits, 'data'],
            y_units: [p.SpatialUnits, 'data'],
            text: [p.StringSpec, { field: "text" }],
            angle: [p.AngleSpec, 0],
            x_offset: [p.NumberSpec, { value: 0 }],
            y_offset: [p.NumberSpec, { value: 0 }],
            source: [p.Instance, function () { return new column_data_source_1.ColumnDataSource(); }],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
        this.override({
            background_fill_color: null,
            border_line_color: null,
        });
    };
    return LabelSet;
}(text_annotation_1.TextAnnotation));
exports.LabelSet = LabelSet;
LabelSet.initClass();
