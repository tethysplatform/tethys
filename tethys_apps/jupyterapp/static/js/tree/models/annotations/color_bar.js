"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var basic_ticker_1 = require("../tickers/basic_ticker");
var basic_tick_formatter_1 = require("../formatters/basic_tick_formatter");
var linear_color_mapper_1 = require("../mappers/linear_color_mapper");
var linear_scale_1 = require("../scales/linear_scale");
var log_scale_1 = require("../scales/log_scale");
var range1d_1 = require("../ranges/range1d");
var p = require("core/properties");
var text_util = require("core/util/text");
var array_1 = require("core/util/array");
var arrayable_1 = require("core/util/arrayable");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
var SHORT_DIM = 25;
var LONG_DIM_MIN_SCALAR = 0.3;
var LONG_DIM_MAX_SCALAR = 0.8;
var ColorBarView = /** @class */ (function (_super) {
    tslib_1.__extends(ColorBarView, _super);
    function ColorBarView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ColorBarView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this._set_canvas_image();
    };
    ColorBarView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.visible.change, function () { return _this.plot_view.request_render(); });
        this.connect(this.model.ticker.change, function () { return _this.plot_view.request_render(); });
        this.connect(this.model.formatter.change, function () { return _this.plot_view.request_render(); });
        if (this.model.color_mapper != null) {
            this.connect(this.model.color_mapper.change, function () {
                _this._set_canvas_image();
                _this.plot_view.request_render();
            });
        }
    };
    ColorBarView.prototype._get_size = function () {
        if (this.model.color_mapper == null)
            return 0;
        var bbox = this.compute_legend_dimensions();
        var side = this.model.panel.side;
        switch (side) {
            case "above":
            case "below":
                return bbox.height;
            case "left":
            case "right":
                return bbox.width;
            default:
                throw new Error("unreachable code");
        }
    };
    ColorBarView.prototype._set_canvas_image = function () {
        var _a, _b;
        if (this.model.color_mapper == null)
            return;
        var palette = this.model.color_mapper.palette;
        if (this.model.orientation == 'vertical')
            palette = array_1.reversed(palette);
        var w, h;
        switch (this.model.orientation) {
            case "vertical": {
                _a = [1, palette.length], w = _a[0], h = _a[1];
                break;
            }
            case "horizontal": {
                _b = [palette.length, 1], w = _b[0], h = _b[1];
                break;
            }
            default:
                throw new Error("unreachable code");
        }
        var canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        var image_ctx = canvas.getContext('2d');
        var image_data = image_ctx.getImageData(0, 0, w, h);
        // We always want to draw the entire palette linearly, so we create a new
        // LinearColorMapper instance and map a monotonic range of values with
        // length = palette.length to get each palette color in order.
        var cmap = new linear_color_mapper_1.LinearColorMapper({ palette: palette }).rgba_mapper;
        var buf8 = cmap.v_compute(array_1.range(0, palette.length));
        image_data.data.set(buf8);
        image_ctx.putImageData(image_data, 0, 0);
        this.image = canvas;
    };
    ColorBarView.prototype.compute_legend_dimensions = function () {
        var image_dimensions = this.model._computed_image_dimensions();
        var _a = [image_dimensions.height, image_dimensions.width], image_height = _a[0], image_width = _a[1];
        var label_extent = this._get_label_extent();
        var title_extent = this.model._title_extent();
        var tick_extent = this.model._tick_extent();
        var padding = this.model.padding;
        var legend_height, legend_width;
        switch (this.model.orientation) {
            case "vertical":
                legend_height = image_height + title_extent + 2 * padding;
                legend_width = image_width + tick_extent + label_extent + 2 * padding;
                break;
            case "horizontal":
                legend_height = image_height + title_extent + tick_extent + label_extent + 2 * padding;
                legend_width = image_width + 2 * padding;
                break;
            default:
                throw new Error("unreachable code");
        }
        return { width: legend_width, height: legend_height };
    };
    ColorBarView.prototype.compute_legend_location = function () {
        var legend_dimensions = this.compute_legend_dimensions();
        var _a = [legend_dimensions.height, legend_dimensions.width], legend_height = _a[0], legend_width = _a[1];
        var legend_margin = this.model.margin;
        var panel = this.model.panel != null ? this.model.panel : this.plot_view.frame;
        var _b = panel.bbox.ranges, hr = _b[0], vr = _b[1];
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
        return { sx: sx, sy: sy };
    };
    ColorBarView.prototype.render = function () {
        if (!this.model.visible || this.model.color_mapper == null)
            return;
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        var _a = this.compute_legend_location(), sx = _a.sx, sy = _a.sy;
        ctx.translate(sx, sy);
        this._draw_bbox(ctx);
        var image_offset = this._get_image_offset();
        ctx.translate(image_offset.x, image_offset.y);
        this._draw_image(ctx);
        if (this.model.color_mapper.low != null && this.model.color_mapper.high != null) {
            var tick_info = this.model.tick_info();
            this._draw_major_ticks(ctx, tick_info);
            this._draw_minor_ticks(ctx, tick_info);
            this._draw_major_labels(ctx, tick_info);
        }
        if (this.model.title)
            this._draw_title(ctx);
        ctx.restore();
    };
    ColorBarView.prototype._draw_bbox = function (ctx) {
        var bbox = this.compute_legend_dimensions();
        ctx.save();
        if (this.visuals.background_fill.doit) {
            this.visuals.background_fill.set_value(ctx);
            ctx.fillRect(0, 0, bbox.width, bbox.height);
        }
        if (this.visuals.border_line.doit) {
            this.visuals.border_line.set_value(ctx);
            ctx.strokeRect(0, 0, bbox.width, bbox.height);
        }
        ctx.restore();
    };
    ColorBarView.prototype._draw_image = function (ctx) {
        var image = this.model._computed_image_dimensions();
        ctx.save();
        ctx.setImageSmoothingEnabled(false);
        ctx.globalAlpha = this.model.scale_alpha;
        ctx.drawImage(this.image, 0, 0, image.width, image.height);
        if (this.visuals.bar_line.doit) {
            this.visuals.bar_line.set_value(ctx);
            ctx.strokeRect(0, 0, image.width, image.height);
        }
        ctx.restore();
    };
    ColorBarView.prototype._draw_major_ticks = function (ctx, tick_info) {
        if (!this.visuals.major_tick_line.doit)
            return;
        var _a = this.model._normals(), nx = _a[0], ny = _a[1];
        var image = this.model._computed_image_dimensions();
        var _b = [image.width * nx, image.height * ny], x_offset = _b[0], y_offset = _b[1];
        var _c = tick_info.coords.major, sx = _c[0], sy = _c[1];
        var tin = this.model.major_tick_in;
        var tout = this.model.major_tick_out;
        ctx.save();
        ctx.translate(x_offset, y_offset);
        this.visuals.major_tick_line.set_value(ctx);
        for (var i = 0, end = sx.length; i < end; i++) {
            ctx.beginPath();
            ctx.moveTo(Math.round(sx[i] + nx * tout), Math.round(sy[i] + ny * tout));
            ctx.lineTo(Math.round(sx[i] - nx * tin), Math.round(sy[i] - ny * tin));
            ctx.stroke();
        }
        ctx.restore();
    };
    ColorBarView.prototype._draw_minor_ticks = function (ctx, tick_info) {
        if (!this.visuals.minor_tick_line.doit)
            return;
        var _a = this.model._normals(), nx = _a[0], ny = _a[1];
        var image = this.model._computed_image_dimensions();
        var _b = [image.width * nx, image.height * ny], x_offset = _b[0], y_offset = _b[1];
        var _c = tick_info.coords.minor, sx = _c[0], sy = _c[1];
        var tin = this.model.minor_tick_in;
        var tout = this.model.minor_tick_out;
        ctx.save();
        ctx.translate(x_offset, y_offset);
        this.visuals.minor_tick_line.set_value(ctx);
        for (var i = 0, end = sx.length; i < end; i++) {
            ctx.beginPath();
            ctx.moveTo(Math.round(sx[i] + nx * tout), Math.round(sy[i] + ny * tout));
            ctx.lineTo(Math.round(sx[i] - nx * tin), Math.round(sy[i] - ny * tin));
            ctx.stroke();
        }
        ctx.restore();
    };
    ColorBarView.prototype._draw_major_labels = function (ctx, tick_info) {
        if (!this.visuals.major_label_text.doit)
            return;
        var _a = this.model._normals(), nx = _a[0], ny = _a[1];
        var image = this.model._computed_image_dimensions();
        var _b = [image.width * nx, image.height * ny], x_offset = _b[0], y_offset = _b[1];
        var standoff = (this.model.label_standoff + this.model._tick_extent());
        var _c = [standoff * nx, standoff * ny], x_standoff = _c[0], y_standoff = _c[1];
        var _d = tick_info.coords.major, sx = _d[0], sy = _d[1];
        var formatted_labels = tick_info.labels.major;
        this.visuals.major_label_text.set_value(ctx);
        ctx.save();
        ctx.translate(x_offset + x_standoff, y_offset + y_standoff);
        for (var i = 0, end = sx.length; i < end; i++) {
            ctx.fillText(formatted_labels[i], Math.round(sx[i] + nx * this.model.label_standoff), Math.round(sy[i] + ny * this.model.label_standoff));
        }
        ctx.restore();
    };
    ColorBarView.prototype._draw_title = function (ctx) {
        if (!this.visuals.title_text.doit)
            return;
        ctx.save();
        this.visuals.title_text.set_value(ctx);
        ctx.fillText(this.model.title, 0, -this.model.title_standoff);
        ctx.restore();
    };
    ColorBarView.prototype._get_label_extent = function () {
        var major_labels = this.model.tick_info().labels.major;
        var label_extent;
        if (this.model.color_mapper.low != null && this.model.color_mapper.high != null && !object_1.isEmpty(major_labels)) {
            var ctx_1 = this.plot_view.canvas_view.ctx;
            ctx_1.save();
            this.visuals.major_label_text.set_value(ctx_1);
            switch (this.model.orientation) {
                case "vertical":
                    label_extent = array_1.max((major_labels.map(function (label) { return ctx_1.measureText(label.toString()).width; })));
                    break;
                case "horizontal":
                    label_extent = text_util.get_text_height(this.visuals.major_label_text.font_value()).height;
                    break;
                default:
                    throw new Error("unreachable code");
            }
            label_extent += this.model.label_standoff;
            ctx_1.restore();
        }
        else
            label_extent = 0;
        return label_extent;
    };
    ColorBarView.prototype._get_image_offset = function () {
        // Returns image offset relative to legend bounding box
        var x = this.model.padding;
        var y = this.model.padding + this.model._title_extent();
        return { x: x, y: y };
    };
    return ColorBarView;
}(annotation_1.AnnotationView));
exports.ColorBarView = ColorBarView;
var ColorBar = /** @class */ (function (_super) {
    tslib_1.__extends(ColorBar, _super);
    function ColorBar(attrs) {
        return _super.call(this, attrs) || this;
    }
    ColorBar.initClass = function () {
        this.prototype.type = 'ColorBar';
        this.prototype.default_view = ColorBarView;
        this.mixins([
            'text:major_label_',
            'text:title_',
            'line:major_tick_',
            'line:minor_tick_',
            'line:border_',
            'line:bar_',
            'fill:background_',
        ]);
        this.define({
            location: [p.Any, 'top_right'],
            orientation: [p.Orientation, 'vertical'],
            title: [p.String,],
            title_standoff: [p.Number, 2],
            width: [p.Any, 'auto'],
            height: [p.Any, 'auto'],
            scale_alpha: [p.Number, 1.0],
            ticker: [p.Instance, function () { return new basic_ticker_1.BasicTicker(); }],
            formatter: [p.Instance, function () { return new basic_tick_formatter_1.BasicTickFormatter(); }],
            major_label_overrides: [p.Any, {}],
            color_mapper: [p.Instance],
            label_standoff: [p.Number, 5],
            margin: [p.Number, 30],
            padding: [p.Number, 10],
            major_tick_in: [p.Number, 5],
            major_tick_out: [p.Number, 0],
            minor_tick_in: [p.Number, 0],
            minor_tick_out: [p.Number, 0],
        });
        this.override({
            background_fill_color: "#ffffff",
            background_fill_alpha: 0.95,
            bar_line_color: null,
            border_line_color: null,
            major_label_text_align: "center",
            major_label_text_baseline: "middle",
            major_label_text_font_size: "8pt",
            major_tick_line_color: "#ffffff",
            minor_tick_line_color: null,
            title_text_font_size: "10pt",
            title_text_font_style: "italic",
        });
    };
    ColorBar.prototype._normals = function () {
        return this.orientation == 'vertical' ? [1, 0] : [0, 1];
    };
    ColorBar.prototype._title_extent = function () {
        var font_value = this.title_text_font + " " + this.title_text_font_size + " " + this.title_text_font_style;
        var title_extent = this.title ? text_util.get_text_height(font_value).height + this.title_standoff : 0;
        return title_extent;
    };
    ColorBar.prototype._tick_extent = function () {
        if (this.color_mapper.low != null && this.color_mapper.high != null)
            return array_1.max([this.major_tick_out, this.minor_tick_out]);
        else
            return 0;
    };
    ColorBar.prototype._computed_image_dimensions = function () {
        /*
        Heuristics to determine ColorBar image dimensions if set to "auto"
    
        Note: Returns the height/width values for the ColorBar's scale image, not
        the dimensions of the entire ColorBar.
    
        If the short dimension (the width of a vertical bar or height of a
        horizontal bar) is set to "auto", the resulting dimension will be set to
        25 px.
    
        For a ColorBar in a side panel with the long dimension (the height of a
        vertical bar or width of a horizontal bar) set to "auto", the
        resulting dimension will be as long as the adjacent frame edge, so that the
        bar "fits" to the plot.
    
        For a ColorBar in the plot frame with the long dimension set to "auto", the
        resulting dimension will be the greater of:
          * The length of the color palette * 25px
          * The parallel frame dimension * 0.30
            (i.e the frame height for a vertical ColorBar)
        But not greater than:
          * The parallel frame dimension * 0.80
        */
        var frame_height = this.plot.plot_canvas.frame._height.value;
        var frame_width = this.plot.plot_canvas.frame._width.value;
        var title_extent = this._title_extent();
        var height, width;
        switch (this.orientation) {
            case "vertical": {
                if (this.height == 'auto') {
                    if (this.panel != null)
                        height = frame_height - 2 * this.padding - title_extent;
                    else {
                        height = array_1.max([this.color_mapper.palette.length * SHORT_DIM, frame_height * LONG_DIM_MIN_SCALAR]);
                        height = array_1.min([height, frame_height * LONG_DIM_MAX_SCALAR - 2 * this.padding - title_extent]);
                    }
                }
                else
                    height = this.height;
                width = this.width == 'auto' ? SHORT_DIM : this.width;
                break;
            }
            case "horizontal": {
                height = this.height == 'auto' ? SHORT_DIM : this.height;
                if (this.width == 'auto') {
                    if (this.panel != null)
                        width = frame_width - 2 * this.padding;
                    else {
                        width = array_1.max([this.color_mapper.palette.length * SHORT_DIM, frame_width * LONG_DIM_MIN_SCALAR]);
                        width = array_1.min([width, frame_width * LONG_DIM_MAX_SCALAR - 2 * this.padding]);
                    }
                }
                else
                    width = this.width;
                break;
            }
            default:
                throw new Error("unreachable code");
        }
        return { width: width, height: height };
    };
    ColorBar.prototype._tick_coordinate_scale = function (scale_length) {
        /*
        Creates and returns a scale instance that maps the `color_mapper` range
        (low to high) to a screen space range equal to the length of the ColorBar's
        scale image. The scale is used to calculate the tick coordinates in screen
        coordinates for plotting purposes.
    
        Note: the type of color_mapper has to match the type of scale (i.e.
        a LinearColorMapper will require a corresponding LinearScale instance).
        */
        var ranges = {
            source_range: new range1d_1.Range1d({
                start: this.color_mapper.low,
                end: this.color_mapper.high,
            }),
            target_range: new range1d_1.Range1d({
                start: 0,
                end: scale_length,
            }),
        };
        switch (this.color_mapper.type) {
            case "LinearColorMapper": return new linear_scale_1.LinearScale(ranges);
            case "LogColorMapper": return new log_scale_1.LogScale(ranges);
            default:
                throw new Error("unreachable code");
        }
    };
    ColorBar.prototype._format_major_labels = function (initial_labels, major_ticks) {
        // XXX: passing null as cross_loc probably means MercatorTickFormatters, etc
        // will not function properly in conjunction with colorbars
        var formatted_labels = this.formatter.doFormat(initial_labels, null);
        for (var i = 0, end = major_ticks.length; i < end; i++) {
            if (major_ticks[i] in this.major_label_overrides)
                formatted_labels[i] = this.major_label_overrides[major_ticks[i]];
        }
        return formatted_labels;
    };
    ColorBar.prototype.tick_info = function () {
        var image_dimensions = this._computed_image_dimensions();
        var scale_length;
        switch (this.orientation) {
            case "vertical": {
                scale_length = image_dimensions.height;
                break;
            }
            case "horizontal": {
                scale_length = image_dimensions.width;
                break;
            }
            default:
                throw new Error("unreachable code");
        }
        var scale = this._tick_coordinate_scale(scale_length);
        var _a = this._normals(), i = _a[0], j = _a[1];
        var _b = [this.color_mapper.low, this.color_mapper.high], start = _b[0], end = _b[1];
        // XXX: passing null as cross_loc probably means MercatorTickers, etc
        // will not function properly in conjunction with colorbars
        var ticks = this.ticker.get_ticks(start, end, null, null, this.ticker.desired_num_ticks);
        var majors = ticks.major;
        var minors = ticks.minor;
        var major_coords = [[], []];
        var minor_coords = [[], []];
        for (var ii = 0, _end = majors.length; ii < _end; ii++) {
            if (majors[ii] < start || majors[ii] > end)
                continue;
            major_coords[i].push(majors[ii]);
            major_coords[j].push(0);
        }
        for (var ii = 0, _end = minors.length; ii < _end; ii++) {
            if (minors[ii] < start || minors[ii] > end)
                continue;
            minor_coords[i].push(minors[ii]);
            minor_coords[j].push(0);
        }
        var labels = { major: this._format_major_labels(major_coords[i], majors) };
        var coords = {
            major: [[], []],
            minor: [[], []],
        };
        coords.major[i] = scale.v_compute(major_coords[i]);
        coords.minor[i] = scale.v_compute(minor_coords[i]);
        coords.major[j] = major_coords[j];
        coords.minor[j] = minor_coords[j];
        // Because we want the scale to be reversed
        if (this.orientation == 'vertical') {
            coords.major[i] = arrayable_1.map(coords.major[i], function (coord) { return scale_length - coord; });
            coords.minor[i] = arrayable_1.map(coords.minor[i], function (coord) { return scale_length - coord; });
        }
        return { coords: coords, labels: labels };
    };
    return ColorBar;
}(annotation_1.Annotation));
exports.ColorBar = ColorBar;
ColorBar.initClass();
