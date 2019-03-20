"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var p = require("core/properties");
var signaling_1 = require("core/signaling");
var text_1 = require("core/util/text");
var bbox_1 = require("core/util/bbox");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
var LegendView = /** @class */ (function (_super) {
    tslib_1.__extends(LegendView, _super);
    function LegendView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LegendView.prototype.cursor = function (_sx, _sy) {
        return this.model.click_policy == "none" ? null : "pointer";
    };
    Object.defineProperty(LegendView.prototype, "legend_padding", {
        get: function () {
            return this.visuals.border_line.line_color.value() != null ? this.model.padding : 0;
        },
        enumerable: true,
        configurable: true
    });
    LegendView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
        this.connect(this.model.item_change, function () { return _this.plot_view.request_render(); });
    };
    LegendView.prototype.compute_legend_bbox = function () {
        var legend_names = this.model.get_legend_names();
        var _a = this.model, glyph_height = _a.glyph_height, glyph_width = _a.glyph_width;
        var _b = this.model, label_height = _b.label_height, label_width = _b.label_width;
        this.max_label_height = array_1.max([text_1.get_text_height(this.visuals.label_text.font_value()).height, label_height, glyph_height]);
        // this is to measure text properties
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        this.visuals.label_text.set_value(ctx);
        this.text_widths = {};
        for (var _i = 0, legend_names_1 = legend_names; _i < legend_names_1.length; _i++) {
            var name_1 = legend_names_1[_i];
            this.text_widths[name_1] = array_1.max([ctx.measureText(name_1).width, label_width]);
        }
        ctx.restore();
        var max_label_width = Math.max(array_1.max(object_1.values(this.text_widths)), 0);
        var legend_margin = this.model.margin;
        var legend_padding = this.legend_padding;
        var legend_spacing = this.model.spacing;
        var label_standoff = this.model.label_standoff;
        var legend_height, legend_width;
        if (this.model.orientation == "vertical") {
            legend_height = legend_names.length * this.max_label_height + Math.max(legend_names.length - 1, 0) * legend_spacing + 2 * legend_padding;
            legend_width = max_label_width + glyph_width + label_standoff + 2 * legend_padding;
        }
        else {
            legend_width = 2 * legend_padding + Math.max(legend_names.length - 1, 0) * legend_spacing;
            for (var name_2 in this.text_widths) {
                var width = this.text_widths[name_2];
                legend_width += array_1.max([width, label_width]) + glyph_width + label_standoff;
            }
            legend_height = this.max_label_height + 2 * legend_padding;
        }
        var panel = this.model.panel != null ? this.model.panel : this.plot_view.frame;
        var _c = panel.bbox.ranges, hr = _c[0], vr = _c[1];
        var location = this.model.location;
        var sx, sy;
        if (types_1.isString(location)) {
            switch (location) {
                case 'top_left':
                    sx = hr.start + legend_margin;
                    sy = vr.start + legend_margin;
                    break;
                case 'top_center':
                    sx = (hr.end + hr.start) / 2 - legend_width / 2;
                    sy = vr.start + legend_margin;
                    break;
                case 'top_right':
                    sx = hr.end - legend_margin - legend_width;
                    sy = vr.start + legend_margin;
                    break;
                case 'bottom_right':
                    sx = hr.end - legend_margin - legend_width;
                    sy = vr.end - legend_margin - legend_height;
                    break;
                case 'bottom_center':
                    sx = (hr.end + hr.start) / 2 - legend_width / 2;
                    sy = vr.end - legend_margin - legend_height;
                    break;
                case 'bottom_left':
                    sx = hr.start + legend_margin;
                    sy = vr.end - legend_margin - legend_height;
                    break;
                case 'center_left':
                    sx = hr.start + legend_margin;
                    sy = (vr.end + vr.start) / 2 - legend_height / 2;
                    break;
                case 'center':
                    sx = (hr.end + hr.start) / 2 - legend_width / 2;
                    sy = (vr.end + vr.start) / 2 - legend_height / 2;
                    break;
                case 'center_right':
                    sx = hr.end - legend_margin - legend_width;
                    sy = (vr.end + vr.start) / 2 - legend_height / 2;
                    break;
                default:
                    throw new Error("unreachable code");
            }
        }
        else if (types_1.isArray(location) && location.length == 2) {
            var vx = location[0], vy = location[1];
            sx = panel.xview.compute(vx);
            sy = panel.yview.compute(vy) - legend_height;
        }
        else
            throw new Error("unreachable code");
        return { x: sx, y: sy, width: legend_width, height: legend_height };
    };
    LegendView.prototype.interactive_bbox = function () {
        var _a = this.compute_legend_bbox(), x = _a.x, y = _a.y, width = _a.width, height = _a.height;
        return new bbox_1.BBox({ x: x, y: y, width: width, height: height });
    };
    LegendView.prototype.interactive_hit = function (sx, sy) {
        var bbox = this.interactive_bbox();
        return bbox.contains(sx, sy);
    };
    LegendView.prototype.on_hit = function (sx, sy) {
        var _a, _b;
        var yoffset;
        var glyph_width = this.model.glyph_width;
        var legend_padding = this.legend_padding;
        var legend_spacing = this.model.spacing;
        var label_standoff = this.model.label_standoff;
        var xoffset = (yoffset = legend_padding);
        var legend_bbox = this.compute_legend_bbox();
        var vertical = this.model.orientation == "vertical";
        for (var _i = 0, _c = this.model.items; _i < _c.length; _i++) {
            var item = _c[_i];
            var labels = item.get_labels_list_from_label_prop();
            for (var _d = 0, labels_1 = labels; _d < labels_1.length; _d++) {
                var label = labels_1[_d];
                var x1 = legend_bbox.x + xoffset;
                var y1 = legend_bbox.y + yoffset;
                var w = void 0, h = void 0;
                if (vertical)
                    _a = [legend_bbox.width - 2 * legend_padding, this.max_label_height], w = _a[0], h = _a[1];
                else
                    _b = [this.text_widths[label] + glyph_width + label_standoff, this.max_label_height], w = _b[0], h = _b[1];
                var bbox = new bbox_1.BBox({ x: x1, y: y1, width: w, height: h });
                if (bbox.contains(sx, sy)) {
                    switch (this.model.click_policy) {
                        case "hide": {
                            for (var _e = 0, _f = item.renderers; _e < _f.length; _e++) {
                                var r = _f[_e];
                                r.visible = !r.visible;
                            }
                            break;
                        }
                        case "mute": {
                            for (var _g = 0, _h = item.renderers; _g < _h.length; _g++) {
                                var r = _h[_g];
                                r.muted = !r.muted;
                            }
                            break;
                        }
                    }
                    return true;
                }
                if (vertical)
                    yoffset += this.max_label_height + legend_spacing;
                else
                    xoffset += this.text_widths[label] + glyph_width + label_standoff + legend_spacing;
            }
        }
        return false;
    };
    LegendView.prototype.render = function () {
        if (!this.model.visible)
            return;
        if (this.model.items.length == 0)
            return;
        // set a backref on render so that items can later signal item_change upates
        // on the model to trigger a re-render
        for (var _i = 0, _a = this.model.items; _i < _a.length; _i++) {
            var item = _a[_i];
            item.legend = this.model;
        }
        var ctx = this.plot_view.canvas_view.ctx;
        var bbox = this.compute_legend_bbox();
        ctx.save();
        this._draw_legend_box(ctx, bbox);
        this._draw_legend_items(ctx, bbox);
        ctx.restore();
    };
    LegendView.prototype._draw_legend_box = function (ctx, bbox) {
        ctx.beginPath();
        ctx.rect(bbox.x, bbox.y, bbox.width, bbox.height);
        this.visuals.background_fill.set_value(ctx);
        ctx.fill();
        if (this.visuals.border_line.doit) {
            this.visuals.border_line.set_value(ctx);
            ctx.stroke();
        }
    };
    LegendView.prototype._draw_legend_items = function (ctx, bbox) {
        var _this = this;
        var _a = this.model, glyph_width = _a.glyph_width, glyph_height = _a.glyph_height;
        var legend_padding = this.legend_padding;
        var legend_spacing = this.model.spacing;
        var label_standoff = this.model.label_standoff;
        var xoffset = legend_padding;
        var yoffset = legend_padding;
        var vertical = this.model.orientation == "vertical";
        var _loop_1 = function (item) {
            var _a, _b;
            var labels = item.get_labels_list_from_label_prop();
            var field = item.get_field_from_label_prop();
            if (labels.length == 0)
                return "continue";
            var active = (function () {
                switch (_this.model.click_policy) {
                    case "none": return true;
                    case "hide": return array_1.all(item.renderers, function (r) { return r.visible; });
                    case "mute": return array_1.all(item.renderers, function (r) { return !r.muted; });
                }
            })();
            for (var _i = 0, labels_2 = labels; _i < labels_2.length; _i++) {
                var label = labels_2[_i];
                var x1 = bbox.x + xoffset;
                var y1 = bbox.y + yoffset;
                var x2 = x1 + glyph_width;
                var y2 = y1 + glyph_height;
                if (vertical)
                    yoffset += this_1.max_label_height + legend_spacing;
                else
                    xoffset += this_1.text_widths[label] + glyph_width + label_standoff + legend_spacing;
                this_1.visuals.label_text.set_value(ctx);
                ctx.fillText(label, x2 + label_standoff, y1 + this_1.max_label_height / 2.0);
                for (var _c = 0, _d = item.renderers; _c < _d.length; _c++) {
                    var r = _d[_c];
                    var view = this_1.plot_view.renderer_views[r.id];
                    view.draw_legend(ctx, x1, x2, y1, y2, field, label, item.index);
                }
                if (!active) {
                    var w = void 0, h = void 0;
                    if (vertical)
                        _a = [bbox.width - 2 * legend_padding, this_1.max_label_height], w = _a[0], h = _a[1];
                    else
                        _b = [this_1.text_widths[label] + glyph_width + label_standoff, this_1.max_label_height], w = _b[0], h = _b[1];
                    ctx.beginPath();
                    ctx.rect(x1, y1, w, h);
                    this_1.visuals.inactive_fill.set_value(ctx);
                    ctx.fill();
                }
            }
        };
        var this_1 = this;
        for (var _i = 0, _b = this.model.items; _i < _b.length; _i++) {
            var item = _b[_i];
            _loop_1(item);
        }
    };
    LegendView.prototype._get_size = function () {
        var bbox = this.compute_legend_bbox();
        switch (this.model.panel.side) {
            case "above":
            case "below":
                return bbox.height + 2 * this.model.margin;
            case "left":
            case "right":
                return bbox.width + 2 * this.model.margin;
        }
    };
    return LegendView;
}(annotation_1.AnnotationView));
exports.LegendView = LegendView;
var Legend = /** @class */ (function (_super) {
    tslib_1.__extends(Legend, _super);
    function Legend(attrs) {
        return _super.call(this, attrs) || this;
    }
    Legend.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.item_change = new signaling_1.Signal0(this, "item_change");
    };
    Legend.initClass = function () {
        this.prototype.type = 'Legend';
        this.prototype.default_view = LegendView;
        this.mixins(['text:label_', 'fill:inactive_', 'line:border_', 'fill:background_']);
        this.define({
            orientation: [p.Orientation, 'vertical'],
            location: [p.Any, 'top_right'],
            label_standoff: [p.Number, 5],
            glyph_height: [p.Number, 20],
            glyph_width: [p.Number, 20],
            label_height: [p.Number, 20],
            label_width: [p.Number, 20],
            margin: [p.Number, 10],
            padding: [p.Number, 10],
            spacing: [p.Number, 3],
            items: [p.Array, []],
            click_policy: [p.Any, "none"],
        });
        this.override({
            border_line_color: "#e5e5e5",
            border_line_alpha: 0.5,
            border_line_width: 1,
            background_fill_color: "#ffffff",
            background_fill_alpha: 0.95,
            inactive_fill_color: "white",
            inactive_fill_alpha: 0.7,
            label_text_font_size: "10pt",
            label_text_baseline: "middle",
        });
    };
    Legend.prototype.get_legend_names = function () {
        var legend_names = [];
        for (var _i = 0, _a = this.items; _i < _a.length; _i++) {
            var item = _a[_i];
            var labels = item.get_labels_list_from_label_prop();
            legend_names.push.apply(legend_names, labels);
        }
        return legend_names;
    };
    return Legend;
}(annotation_1.Annotation));
exports.Legend = Legend;
Legend.initClass();
