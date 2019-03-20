"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var sprintf_js_1 = require("sprintf-js");
var palettes = require("./palettes");
var array_1 = require("../core/util/array");
var types_1 = require("../core/util/types");
var models_1 = require("./models");
function num2hexcolor(num) {
    return sprintf_js_1.sprintf("#%06x", num);
}
function hexcolor2rgb(color) {
    var r = parseInt(color.substr(1, 2), 16);
    var g = parseInt(color.substr(3, 2), 16);
    var b = parseInt(color.substr(5, 2), 16);
    return [r, g, b];
}
function is_dark(_a) {
    var r = _a[0], g = _a[1], b = _a[2];
    var l = 1 - (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return l >= 0.6;
}
function norm_palette(palette) {
    if (palette === void 0) { palette = "Spectral11"; }
    if (types_1.isArray(palette))
        return palette;
    else {
        return palettes[palette].map(num2hexcolor);
    }
}
function pie(data, opts) {
    if (opts === void 0) { opts = {}; }
    var labels = [];
    var values = [];
    for (var i = 0; i < Math.min(data.labels.length, data.values.length); i++) {
        if (data.values[i] > 0) {
            labels.push(data.labels[i]);
            values.push(data.values[i]);
        }
    }
    var start_angle = opts.start_angle != null ? opts.start_angle : 0;
    var end_angle = opts.end_angle != null ? opts.end_angle : (start_angle + 2 * Math.PI);
    var angle_span = Math.abs(end_angle - start_angle);
    var to_radians = function (x) { return angle_span * x; };
    var total_value = array_1.sum(values);
    var normalized_values = values.map(function (v) { return v / total_value; });
    var cumulative_values = array_1.cumsum(normalized_values);
    var end_angles = cumulative_values.map(function (v) { return start_angle + to_radians(v); });
    var start_angles = [start_angle].concat(end_angles.slice(0, -1));
    var half_angles = array_1.zip(start_angles, end_angles).map(function (_a) {
        var start = _a[0], end = _a[1];
        return (start + end) / 2;
    });
    var cx;
    var cy;
    if (opts.center == null) {
        cx = 0;
        cy = 0;
    }
    else if (types_1.isArray(opts.center)) {
        cx = opts.center[0];
        cy = opts.center[1];
    }
    else {
        cx = opts.center.x;
        cy = opts.center.y;
    }
    var inner_radius = opts.inner_radius != null ? opts.inner_radius : 0;
    var outer_radius = opts.outer_radius != null ? opts.outer_radius : 1;
    var palette = norm_palette(opts.palette);
    var colors = [];
    for (var i = 0; i < normalized_values.length; i++)
        colors.push(palette[i % palette.length]);
    var text_colors = colors.map(function (c) { return is_dark(hexcolor2rgb(c)) ? "white" : "black"; });
    function to_cartesian(r, alpha) {
        return [r * Math.cos(alpha), r * Math.sin(alpha)];
    }
    var half_radius = (inner_radius + outer_radius) / 2;
    var _a = array_1.unzip(half_angles.map(function (half_angle) { return to_cartesian(half_radius, half_angle); })), text_cx = _a[0], text_cy = _a[1];
    text_cx = text_cx.map(function (x) { return x + cx; });
    text_cy = text_cy.map(function (y) { return y + cy; });
    var text_angles = half_angles.map(function (a) {
        if (a >= Math.PI / 2 && a <= 3 * Math.PI / 2)
            return a + Math.PI;
        else
            return a;
    });
    var source = new models_1.ColumnDataSource({
        data: {
            labels: labels,
            values: values,
            percentages: normalized_values.map(function (v) { return sprintf_js_1.sprintf("%.2f%%", v * 100); }),
            start_angles: start_angles,
            end_angles: end_angles,
            text_angles: text_angles,
            colors: colors,
            text_colors: text_colors,
            text_cx: text_cx,
            text_cy: text_cy,
        },
    });
    var g1 = new models_1.AnnularWedge({
        x: cx, y: cy,
        inner_radius: inner_radius, outer_radius: outer_radius,
        start_angle: { field: "start_angles" }, end_angle: { field: "end_angles" },
        line_color: null, line_width: 1, fill_color: { field: "colors" },
    });
    var h1 = new models_1.AnnularWedge({
        x: cx, y: cy,
        inner_radius: inner_radius, outer_radius: outer_radius,
        start_angle: { field: "start_angles" }, end_angle: { field: "end_angles" },
        line_color: null, line_width: 1, fill_color: { field: "colors" }, fill_alpha: 0.8,
    });
    var r1 = new models_1.GlyphRenderer({
        data_source: source,
        glyph: g1,
        hover_glyph: h1,
    });
    var g2 = new models_1.Text({
        x: { field: "text_cx" }, y: { field: "text_cy" },
        text: { field: opts.slice_labels || "labels" },
        angle: { field: "text_angles" },
        text_align: "center", text_baseline: "middle",
        text_color: { field: "text_colors" }, text_font_size: "9pt",
    });
    var r2 = new models_1.GlyphRenderer({
        data_source: source,
        glyph: g2,
    });
    var xdr = new models_1.DataRange1d({ renderers: [r1], range_padding: 0.2 });
    var ydr = new models_1.DataRange1d({ renderers: [r1], range_padding: 0.2 });
    var plot = new models_1.Plot({ x_range: xdr, y_range: ydr });
    if (opts.width != null)
        plot.plot_width = opts.width;
    if (opts.height != null)
        plot.plot_height = opts.height;
    plot.add_renderers(r1, r2);
    var tooltip = "<div>@labels</div><div><b>@values</b> (@percentages)</div>";
    var hover = new models_1.HoverTool({ renderers: [r1], tooltips: tooltip });
    plot.add_tools(hover);
    return plot;
}
exports.pie = pie;
function bar(data, opts) {
    if (opts === void 0) { opts = {}; }
    var _a, _b, _c, _d, _e;
    var column_names = data[0];
    var rows = data.slice(1);
    var columns = column_names.map(function (_) { return []; });
    for (var _i = 0, rows_1 = rows; _i < rows_1.length; _i++) {
        var row = rows_1[_i];
        for (var i = 0; i < row.length; i++) {
            columns[i].push(row[i]);
        }
    }
    var labels = columns[0].map(function (v) { return v.toString(); });
    columns = columns.slice(1);
    var yaxis = new models_1.CategoricalAxis();
    var ydr = new models_1.FactorRange({ factors: labels });
    var yscale = new models_1.CategoricalScale();
    var xformatter;
    if (opts.axis_number_format != null)
        xformatter = new models_1.NumeralTickFormatter({ format: opts.axis_number_format });
    else
        xformatter = new models_1.BasicTickFormatter();
    var xaxis = new models_1.LinearAxis({ formatter: xformatter });
    var xdr = new models_1.DataRange1d({ start: 0 });
    var xscale = new models_1.LinearScale();
    var palette = norm_palette(opts.palette);
    var stacked = opts.stacked != null ? opts.stacked : false;
    var orientation = opts.orientation != null ? opts.orientation : "horizontal";
    var renderers = [];
    if (stacked) {
        var left = [];
        var right = [];
        var _loop_1 = function (i) {
            var bottom = [];
            var top_1 = [];
            for (var j = 0; j < labels.length; j++) {
                var label = labels[j];
                if (i == 0) {
                    left.push(0);
                    right.push(columns[i][j]);
                }
                else {
                    left[j] += columns[i - 1][j];
                    right[j] += columns[i][j];
                }
                bottom.push([label, -0.5]);
                top_1.push([label, 0.5]);
            }
            var source = new models_1.ColumnDataSource({
                data: {
                    left: array_1.copy(left),
                    right: array_1.copy(right),
                    top: top_1,
                    bottom: bottom,
                    labels: labels,
                    values: columns[i],
                    columns: columns[i].map(function (_) { return column_names[i + 1]; }),
                },
            });
            var g1 = new models_1.Quad({
                left: { field: "left" }, bottom: { field: "bottom" },
                right: { field: "right" }, top: { field: "top" },
                line_color: null, fill_color: palette[i % palette.length],
            });
            var r1 = new models_1.GlyphRenderer({ data_source: source, glyph: g1 });
            renderers.push(r1);
        };
        for (var i = 0; i < columns.length; i++) {
            _loop_1(i);
        }
    }
    else {
        var dy = 1 / columns.length;
        var _loop_2 = function (i) {
            var left = [];
            var right = [];
            var bottom = [];
            var top_2 = [];
            for (var j = 0; j < labels.length; j++) {
                var label = labels[j];
                left.push(0);
                right.push(columns[i][j]);
                bottom.push([label, i * dy - 0.5]);
                top_2.push([label, (i + 1) * dy - 0.5]);
            }
            var source = new models_1.ColumnDataSource({
                data: {
                    left: left,
                    right: right,
                    top: top_2,
                    bottom: bottom,
                    labels: labels,
                    values: columns[i],
                    columns: columns[i].map(function (_) { return column_names[i + 1]; }),
                },
            });
            var g1 = new models_1.Quad({
                left: { field: "left" }, bottom: { field: "bottom" },
                right: { field: "right" }, top: { field: "top" },
                line_color: null, fill_color: palette[i % palette.length],
            });
            var r1 = new models_1.GlyphRenderer({ data_source: source, glyph: g1 });
            renderers.push(r1);
        };
        for (var i = 0; i < columns.length; i++) {
            _loop_2(i);
        }
    }
    if (orientation == "vertical") {
        _a = [ydr, xdr], xdr = _a[0], ydr = _a[1];
        _b = [yaxis, xaxis], xaxis = _b[0], yaxis = _b[1];
        _c = [yscale, xscale], xscale = _c[0], yscale = _c[1];
        for (var _f = 0, renderers_1 = renderers; _f < renderers_1.length; _f++) {
            var r = renderers_1[_f];
            var data_1 = r.data_source.data;
            _d = [data_1.bottom, data_1.left], data_1.left = _d[0], data_1.bottom = _d[1];
            _e = [data_1.top, data_1.right], data_1.right = _e[0], data_1.top = _e[1];
        }
    }
    var plot = new models_1.Plot({ x_range: xdr, y_range: ydr, x_scale: xscale, y_scale: yscale });
    if (opts.width != null)
        plot.plot_width = opts.width;
    if (opts.height != null)
        plot.plot_height = opts.height;
    plot.add_renderers.apply(plot, renderers);
    plot.add_layout(yaxis, "left");
    plot.add_layout(xaxis, "below");
    var tooltip = "<div>@labels</div><div>@columns:&nbsp<b>@values</b></div>";
    var anchor;
    var attachment;
    if (orientation == "horizontal") {
        anchor = "center_right";
        attachment = "horizontal";
    }
    else {
        anchor = "top_center";
        attachment = "vertical";
    }
    var hover = new models_1.HoverTool({
        renderers: renderers,
        tooltips: tooltip,
        point_policy: "snap_to_data",
        anchor: anchor,
        attachment: attachment,
    });
    plot.add_tools(hover);
    return plot;
}
exports.bar = bar;
