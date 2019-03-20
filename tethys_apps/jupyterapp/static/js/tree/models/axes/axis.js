"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var guide_renderer_1 = require("../renderers/guide_renderer");
var p = require("core/properties");
var side_panel_1 = require("core/layout/side_panel");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var factor_range_1 = require("models/ranges/factor_range");
var abs = Math.abs, min = Math.min, max = Math.max;
var AxisView = /** @class */ (function (_super) {
    tslib_1.__extends(AxisView, _super);
    function AxisView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AxisView.prototype.render = function () {
        if (!this.model.visible)
            return;
        var extents = {
            tick: this._tick_extent(),
            tick_label: this._tick_label_extents(),
            axis_label: this._axis_label_extent(),
        };
        var tick_coords = this.model.tick_coords;
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        this._draw_rule(ctx, extents);
        this._draw_major_ticks(ctx, extents, tick_coords);
        this._draw_minor_ticks(ctx, extents, tick_coords);
        this._draw_major_labels(ctx, extents, tick_coords);
        this._draw_axis_label(ctx, extents, tick_coords);
        if (this._render != null)
            this._render(ctx, extents, tick_coords);
        ctx.restore();
    };
    AxisView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
    };
    AxisView.prototype.get_size = function () {
        return this.model.visible ? Math.round(this._get_size()) : 0;
    };
    AxisView.prototype._get_size = function () {
        if (this.model.fixed_location != null) {
            return 0;
        }
        return this._tick_extent() + this._tick_label_extent() + this._axis_label_extent();
    };
    Object.defineProperty(AxisView.prototype, "needs_clip", {
        get: function () {
            return this.model.fixed_location != null;
        },
        enumerable: true,
        configurable: true
    });
    // drawing sub functions -----------------------------------------------------
    AxisView.prototype._draw_rule = function (ctx, _extents) {
        if (!this.visuals.axis_line.doit)
            return;
        var _a = this.model.rule_coords, xs = _a[0], ys = _a[1];
        var _b = this.plot_view.map_to_screen(xs, ys, this.model.x_range_name, this.model.y_range_name), sxs = _b[0], sys = _b[1];
        var _c = this.model.normals, nx = _c[0], ny = _c[1];
        var _d = this.model.offsets, xoff = _d[0], yoff = _d[1];
        this.visuals.axis_line.set_value(ctx);
        ctx.beginPath();
        ctx.moveTo(Math.round(sxs[0] + nx * xoff), Math.round(sys[0] + ny * yoff));
        for (var i = 1; i < sxs.length; i++) {
            var sx = Math.round(sxs[i] + nx * xoff);
            var sy = Math.round(sys[i] + ny * yoff);
            ctx.lineTo(sx, sy);
        }
        ctx.stroke();
    };
    AxisView.prototype._draw_major_ticks = function (ctx, _extents, tick_coords) {
        var tin = this.model.major_tick_in;
        var tout = this.model.major_tick_out;
        var visuals = this.visuals.major_tick_line;
        this._draw_ticks(ctx, tick_coords.major, tin, tout, visuals);
    };
    AxisView.prototype._draw_minor_ticks = function (ctx, _extents, tick_coords) {
        var tin = this.model.minor_tick_in;
        var tout = this.model.minor_tick_out;
        var visuals = this.visuals.minor_tick_line;
        this._draw_ticks(ctx, tick_coords.minor, tin, tout, visuals);
    };
    AxisView.prototype._draw_major_labels = function (ctx, extents, tick_coords) {
        var coords = tick_coords.major;
        var labels = this.model.compute_labels(coords[this.model.dimension]);
        var orient = this.model.major_label_orientation;
        var standoff = extents.tick + this.model.major_label_standoff;
        var visuals = this.visuals.major_label_text;
        this._draw_oriented_labels(ctx, labels, coords, orient, this.model.panel.side, standoff, visuals);
    };
    AxisView.prototype._draw_axis_label = function (ctx, extents, _tick_coords) {
        if (this.model.axis_label == null || this.model.axis_label.length == 0 || this.model.fixed_location != null)
            return;
        var sx;
        var sy;
        switch (this.model.panel.side) {
            case "above":
                sx = this.model.panel._hcenter.value;
                sy = this.model.panel._bottom.value;
                break;
            case "below":
                sx = this.model.panel._hcenter.value;
                sy = this.model.panel._top.value;
                break;
            case "left":
                sx = this.model.panel._right.value;
                sy = this.model.panel._vcenter.value;
                break;
            case "right":
                sx = this.model.panel._left.value;
                sy = this.model.panel._vcenter.value;
                break;
            default:
                throw new Error("unknown side: " + this.model.panel.side);
        }
        var coords = [[sx], [sy]];
        var standoff = extents.tick + array_1.sum(extents.tick_label) + this.model.axis_label_standoff;
        var visuals = this.visuals.axis_label_text;
        this._draw_oriented_labels(ctx, [this.model.axis_label], coords, 'parallel', this.model.panel.side, standoff, visuals, "screen");
    };
    AxisView.prototype._draw_ticks = function (ctx, coords, tin, tout, visuals) {
        if (!visuals.doit)
            return;
        var x = coords[0], y = coords[1];
        var _a = this.plot_view.map_to_screen(x, y, this.model.x_range_name, this.model.y_range_name), sxs = _a[0], sys = _a[1];
        var _b = this.model.normals, nx = _b[0], ny = _b[1];
        var _c = this.model.offsets, xoff = _c[0], yoff = _c[1];
        var _d = [nx * (xoff - tin), ny * (yoff - tin)], nxin = _d[0], nyin = _d[1];
        var _e = [nx * (xoff + tout), ny * (yoff + tout)], nxout = _e[0], nyout = _e[1];
        visuals.set_value(ctx);
        for (var i = 0; i < sxs.length; i++) {
            var sx0 = Math.round(sxs[i] + nxout);
            var sy0 = Math.round(sys[i] + nyout);
            var sx1 = Math.round(sxs[i] + nxin);
            var sy1 = Math.round(sys[i] + nyin);
            ctx.beginPath();
            ctx.moveTo(sx0, sy0);
            ctx.lineTo(sx1, sy1);
            ctx.stroke();
        }
    };
    AxisView.prototype._draw_oriented_labels = function (ctx, labels, coords, orient, _side, standoff, visuals, units) {
        if (units === void 0) { units = "data"; }
        var _a, _b, _c;
        if (!visuals.doit || labels.length == 0)
            return;
        var sxs, sys;
        var xoff, yoff;
        if (units == "screen") {
            sxs = coords[0], sys = coords[1];
            _a = [0, 0], xoff = _a[0], yoff = _a[1];
        }
        else {
            var dxs = coords[0], dys = coords[1];
            _b = this.plot_view.map_to_screen(dxs, dys, this.model.x_range_name, this.model.y_range_name), sxs = _b[0], sys = _b[1];
            _c = this.model.offsets, xoff = _c[0], yoff = _c[1];
        }
        var _d = this.model.normals, nx = _d[0], ny = _d[1];
        var nxd = nx * (xoff + standoff);
        var nyd = ny * (yoff + standoff);
        visuals.set_value(ctx);
        this.model.panel.apply_label_text_heuristics(ctx, orient);
        var angle;
        if (types_1.isString(orient))
            angle = this.model.panel.get_label_angle_heuristic(orient);
        else
            angle = -orient;
        for (var i = 0; i < sxs.length; i++) {
            var sx = Math.round(sxs[i] + nxd);
            var sy = Math.round(sys[i] + nyd);
            ctx.translate(sx, sy);
            ctx.rotate(angle);
            ctx.fillText(labels[i], 0, 0);
            ctx.rotate(-angle);
            ctx.translate(-sx, -sy);
        }
    };
    // extents sub functions -----------------------------------------------------
    /*protected*/ AxisView.prototype._axis_label_extent = function () {
        if (this.model.axis_label == null || this.model.axis_label == "")
            return 0;
        var standoff = this.model.axis_label_standoff;
        var visuals = this.visuals.axis_label_text;
        return this._oriented_labels_extent([this.model.axis_label], "parallel", this.model.panel.side, standoff, visuals);
    };
    /*protected*/ AxisView.prototype._tick_extent = function () {
        return this.model.major_tick_out;
    };
    /*protected*/ AxisView.prototype._tick_label_extent = function () {
        return array_1.sum(this._tick_label_extents());
    };
    AxisView.prototype._tick_label_extents = function () {
        var coords = this.model.tick_coords.major;
        var labels = this.model.compute_labels(coords[this.model.dimension]);
        var orient = this.model.major_label_orientation;
        var standoff = this.model.major_label_standoff;
        var visuals = this.visuals.major_label_text;
        return [this._oriented_labels_extent(labels, orient, this.model.panel.side, standoff, visuals)];
    };
    AxisView.prototype._oriented_labels_extent = function (labels, orient, side, standoff, visuals) {
        if (labels.length == 0)
            return 0;
        var ctx = this.plot_view.canvas_view.ctx;
        visuals.set_value(ctx);
        var hscale;
        var angle;
        if (types_1.isString(orient)) {
            hscale = 1;
            angle = this.model.panel.get_label_angle_heuristic(orient);
        }
        else {
            hscale = 2;
            angle = -orient;
        }
        angle = Math.abs(angle);
        var c = Math.cos(angle);
        var s = Math.sin(angle);
        var extent = 0;
        for (var i = 0; i < labels.length; i++) {
            var w = ctx.measureText(labels[i]).width * 1.1;
            var h = ctx.measureText(labels[i]).ascent * 0.9;
            var val = void 0;
            if (side == "above" || side == "below")
                val = w * s + (h / hscale) * c;
            else
                val = w * c + (h / hscale) * s;
            // update extent if current value is larger
            if (val > extent)
                extent = val;
        }
        // only apply the standoff if we already have non-zero extent
        if (extent > 0)
            extent += standoff;
        return extent;
    };
    return AxisView;
}(guide_renderer_1.GuideRendererView));
exports.AxisView = AxisView;
var Axis = /** @class */ (function (_super) {
    tslib_1.__extends(Axis, _super);
    function Axis(attrs) {
        return _super.call(this, attrs) || this;
    }
    Axis.initClass = function () {
        this.prototype.type = "Axis";
        this.prototype.default_view = AxisView;
        this.mixins([
            'line:axis_',
            'line:major_tick_',
            'line:minor_tick_',
            'text:major_label_',
            'text:axis_label_',
        ]);
        this.define({
            bounds: [p.Any, 'auto'],
            ticker: [p.Instance, null],
            formatter: [p.Instance, null],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
            axis_label: [p.String, ''],
            axis_label_standoff: [p.Int, 5],
            major_label_standoff: [p.Int, 5],
            major_label_orientation: [p.Any, "horizontal"],
            major_label_overrides: [p.Any, {}],
            major_tick_in: [p.Number, 2],
            major_tick_out: [p.Number, 6],
            minor_tick_in: [p.Number, 0],
            minor_tick_out: [p.Number, 4],
            fixed_location: [p.Any, null],
        });
        this.override({
            axis_line_color: 'black',
            major_tick_line_color: 'black',
            minor_tick_line_color: 'black',
            major_label_text_font_size: "8pt",
            major_label_text_align: "center",
            major_label_text_baseline: "alphabetic",
            axis_label_text_font_size: "10pt",
            axis_label_text_font_style: "italic",
        });
    };
    Axis.prototype.add_panel = function (side) {
        this.panel = new side_panel_1.SidePanel({ side: side });
        this.panel.attach_document(this.document); // XXX!
    };
    Object.defineProperty(Axis.prototype, "normals", {
        get: function () {
            return this.panel.normals;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Axis.prototype, "dimension", {
        get: function () {
            return this.panel.dimension;
        },
        enumerable: true,
        configurable: true
    });
    Axis.prototype.compute_labels = function (ticks) {
        var labels = this.formatter.doFormat(ticks, this);
        for (var i = 0; i < ticks.length; i++) {
            if (ticks[i] in this.major_label_overrides)
                labels[i] = this.major_label_overrides[ticks[i]];
        }
        return labels;
    };
    Object.defineProperty(Axis.prototype, "offsets", {
        get: function () {
            var frame = this.plot.plot_canvas.frame;
            var _a = [0, 0], xoff = _a[0], yoff = _a[1];
            switch (this.panel.side) {
                case "below":
                    yoff = abs(this.panel._top.value - frame._bottom.value);
                    break;
                case "above":
                    yoff = abs(this.panel._bottom.value - frame._top.value);
                    break;
                case "right":
                    xoff = abs(this.panel._left.value - frame._right.value);
                    break;
                case "left":
                    xoff = abs(this.panel._right.value - frame._left.value);
                    break;
            }
            return [xoff, yoff];
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Axis.prototype, "ranges", {
        get: function () {
            var i = this.dimension;
            var j = (i + 1) % 2;
            var frame = this.plot.plot_canvas.frame;
            var ranges = [
                frame.x_ranges[this.x_range_name],
                frame.y_ranges[this.y_range_name],
            ];
            return [ranges[i], ranges[j]];
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Axis.prototype, "computed_bounds", {
        get: function () {
            var range = this.ranges[0];
            var user_bounds = this.bounds; // XXX: ? 'auto'
            var range_bounds = [range.min, range.max];
            if (user_bounds == 'auto')
                return [range.min, range.max];
            else if (types_1.isArray(user_bounds)) {
                var start = void 0;
                var end = void 0;
                var user_start = user_bounds[0], user_end = user_bounds[1];
                var range_start = range_bounds[0], range_end = range_bounds[1];
                if (abs(user_start - user_end) > abs(range_start - range_end)) {
                    start = max(min(user_start, user_end), range_start);
                    end = min(max(user_start, user_end), range_end);
                }
                else {
                    start = min(user_start, user_end);
                    end = max(user_start, user_end);
                }
                return [start, end];
            }
            else
                throw new Error("user bounds '" + user_bounds + "' not understood");
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Axis.prototype, "rule_coords", {
        get: function () {
            var i = this.dimension;
            var j = (i + 1) % 2;
            var range = this.ranges[0];
            var _a = this.computed_bounds, start = _a[0], end = _a[1];
            var xs = new Array(2);
            var ys = new Array(2);
            var coords = [xs, ys];
            coords[i][0] = Math.max(start, range.min);
            coords[i][1] = Math.min(end, range.max);
            if (coords[i][0] > coords[i][1])
                coords[i][0] = coords[i][1] = NaN;
            coords[j][0] = this.loc;
            coords[j][1] = this.loc;
            return coords;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Axis.prototype, "tick_coords", {
        get: function () {
            var i = this.dimension;
            var j = (i + 1) % 2;
            var range = this.ranges[0];
            var _a = this.computed_bounds, start = _a[0], end = _a[1];
            var ticks = this.ticker.get_ticks(start, end, range, this.loc, {});
            var majors = ticks.major;
            var minors = ticks.minor;
            var xs = [];
            var ys = [];
            var coords = [xs, ys];
            var minor_xs = [];
            var minor_ys = [];
            var minor_coords = [minor_xs, minor_ys];
            var _b = [range.min, range.max], range_min = _b[0], range_max = _b[1];
            for (var ii = 0; ii < majors.length; ii++) {
                if (majors[ii] < range_min || majors[ii] > range_max)
                    continue;
                coords[i].push(majors[ii]);
                coords[j].push(this.loc);
            }
            for (var ii = 0; ii < minors.length; ii++) {
                if (minors[ii] < range_min || minors[ii] > range_max)
                    continue;
                minor_coords[i].push(minors[ii]);
                minor_coords[j].push(this.loc);
            }
            return {
                major: coords,
                minor: minor_coords,
            };
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Axis.prototype, "loc", {
        get: function () {
            if (this.fixed_location != null) {
                if (types_1.isNumber(this.fixed_location)) {
                    return this.fixed_location;
                }
                var _a = this.ranges, cross_range_1 = _a[1];
                if (cross_range_1 instanceof factor_range_1.FactorRange) {
                    return cross_range_1.synthetic(this.fixed_location);
                }
                throw new Error("unexpected");
            }
            var _b = this.ranges, cross_range = _b[1];
            switch (this.panel.side) {
                case 'left':
                case 'below':
                    return cross_range.start;
                case 'right':
                case 'above':
                    return cross_range.end;
            }
        },
        enumerable: true,
        configurable: true
    });
    return Axis;
}(guide_renderer_1.GuideRenderer));
exports.Axis = Axis;
Axis.initClass();
