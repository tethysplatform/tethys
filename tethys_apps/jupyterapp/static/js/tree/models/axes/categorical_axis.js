"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var axis_1 = require("./axis");
var categorical_ticker_1 = require("../tickers/categorical_ticker");
var categorical_tick_formatter_1 = require("../formatters/categorical_tick_formatter");
var p = require("core/properties");
var CategoricalAxisView = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalAxisView, _super);
    function CategoricalAxisView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CategoricalAxisView.prototype._render = function (ctx, extents, tick_coords) {
        this._draw_group_separators(ctx, extents, tick_coords);
    };
    CategoricalAxisView.prototype._draw_group_separators = function (ctx, _extents, _tick_coords) {
        var _a;
        var range = this.model.ranges[0];
        var _b = this.model.computed_bounds, start = _b[0], end = _b[1];
        if (!range.tops || range.tops.length < 2 || !this.visuals.separator_line.doit)
            return;
        var dim = this.model.dimension;
        var alt = (dim + 1) % 2;
        var coords = [[], []];
        var ind = 0;
        for (var i = 0; i < range.tops.length - 1; i++) {
            var first = void 0, last = void 0;
            for (var j = ind; j < range.factors.length; j++) {
                if (range.factors[j][0] == range.tops[i + 1]) {
                    _a = [range.factors[j - 1], range.factors[j]], first = _a[0], last = _a[1];
                    ind = j;
                    break;
                }
            }
            var pt = (range.synthetic(first) + range.synthetic(last)) / 2;
            if (pt > start && pt < end) {
                coords[dim].push(pt);
                coords[alt].push(this.model.loc);
            }
        }
        var tex = this._tick_label_extent();
        this._draw_ticks(ctx, coords, -3, (tex - 6), this.visuals.separator_line);
    };
    CategoricalAxisView.prototype._draw_major_labels = function (ctx, extents, _tick_coords) {
        var info = this._get_factor_info();
        var standoff = extents.tick + this.model.major_label_standoff;
        for (var i = 0; i < info.length; i++) {
            var _a = info[i], labels = _a[0], coords = _a[1], orient = _a[2], visuals = _a[3];
            this._draw_oriented_labels(ctx, labels, coords, orient, this.model.panel.side, standoff, visuals);
            standoff += extents.tick_label[i];
        }
    };
    CategoricalAxisView.prototype._tick_label_extents = function () {
        var info = this._get_factor_info();
        var extents = [];
        for (var _i = 0, info_1 = info; _i < info_1.length; _i++) {
            var _a = info_1[_i], labels = _a[0], orient = _a[2], visuals = _a[3];
            var extent = this._oriented_labels_extent(labels, orient, this.model.panel.side, this.model.major_label_standoff, visuals);
            extents.push(extent);
        }
        return extents;
    };
    CategoricalAxisView.prototype._get_factor_info = function () {
        var range = this.model.ranges[0];
        var _a = this.model.computed_bounds, start = _a[0], end = _a[1];
        var loc = this.model.loc;
        var ticks = this.model.ticker.get_ticks(start, end, range, loc, {});
        var coords = this.model.tick_coords;
        var info = [];
        if (range.levels == 1) {
            var labels = this.model.formatter.doFormat(ticks.major, this.model);
            info.push([labels, coords.major, this.model.major_label_orientation, this.visuals.major_label_text]);
        }
        else if (range.levels == 2) {
            var labels = this.model.formatter.doFormat(ticks.major.map(function (x) { return x[1]; }), this.model);
            info.push([labels, coords.major, this.model.major_label_orientation, this.visuals.major_label_text]);
            info.push([ticks.tops, coords.tops, this.model.group_label_orientation, this.visuals.group_text]);
        }
        else if (range.levels == 3) {
            var labels = this.model.formatter.doFormat(ticks.major.map(function (x) { return x[2]; }), this.model);
            var mid_labels = ticks.mids.map(function (x) { return x[1]; });
            info.push([labels, coords.major, this.model.major_label_orientation, this.visuals.major_label_text]);
            info.push([mid_labels, coords.mids, this.model.subgroup_label_orientation, this.visuals.subgroup_text]);
            info.push([ticks.tops, coords.tops, this.model.group_label_orientation, this.visuals.group_text]);
        }
        return info;
    };
    return CategoricalAxisView;
}(axis_1.AxisView));
exports.CategoricalAxisView = CategoricalAxisView;
var CategoricalAxis = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalAxis, _super);
    function CategoricalAxis(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalAxis.initClass = function () {
        this.prototype.type = "CategoricalAxis";
        this.prototype.default_view = CategoricalAxisView;
        this.mixins([
            "line:separator_",
            "text:group_",
            "text:subgroup_",
        ]);
        this.define({
            group_label_orientation: [p.Any, "parallel"],
            subgroup_label_orientation: [p.Any, "parallel"],
        });
        this.override({
            ticker: function () { return new categorical_ticker_1.CategoricalTicker(); },
            formatter: function () { return new categorical_tick_formatter_1.CategoricalTickFormatter(); },
            separator_line_color: "lightgrey",
            separator_line_width: 2,
            group_text_font_style: "bold",
            group_text_font_size: "8pt",
            group_text_color: "grey",
            subgroup_text_font_style: "bold",
            subgroup_text_font_size: "8pt",
        });
    };
    Object.defineProperty(CategoricalAxis.prototype, "tick_coords", {
        get: function () {
            var _this = this;
            var i = this.dimension;
            var j = (i + 1) % 2;
            var range = this.ranges[0];
            var _a = this.computed_bounds, start = _a[0], end = _a[1];
            var ticks = this.ticker.get_ticks(start, end, range, this.loc, {});
            var coords = {
                major: [[], []],
                mids: [[], []],
                tops: [[], []],
                minor: [[], []],
            };
            coords.major[i] = ticks.major;
            coords.major[j] = ticks.major.map(function (_x) { return _this.loc; });
            if (range.levels == 3)
                coords.mids[i] = ticks.mids;
            coords.mids[j] = ticks.mids.map(function (_x) { return _this.loc; });
            if (range.levels > 1)
                coords.tops[i] = ticks.tops;
            coords.tops[j] = ticks.tops.map(function (_x) { return _this.loc; });
            return coords;
        },
        enumerable: true,
        configurable: true
    });
    return CategoricalAxis;
}(axis_1.Axis));
exports.CategoricalAxis = CategoricalAxis;
CategoricalAxis.initClass();
