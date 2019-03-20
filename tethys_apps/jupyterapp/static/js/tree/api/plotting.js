"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var sprintf_js_1 = require("sprintf-js");
var document_1 = require("../document");
var embed = require("../embed");
var embed_1 = require("../embed");
var models = require("./models");
var dom_1 = require("../core/dom");
var string_1 = require("../core/util/string");
var eq_1 = require("../core/util/eq");
var array_1 = require("../core/util/array");
var object_1 = require("../core/util/object");
var types_1 = require("../core/util/types");
var models_1 = require("./models");
var legend_1 = require("models/annotations/legend");
var gridplot_1 = require("./gridplot");
exports.gridplot = gridplot_1.gridplot;
var _default_tooltips = [
    ["index", "$index"],
    ["data (x, y)", "($x, $y)"],
    ["screen (x, y)", "($sx, $sy)"],
];
var _default_tools = ["pan", "wheel_zoom", "box_zoom", "save", "reset", "help"];
var _known_tools = {
    pan: function () { return new models.PanTool({ dimensions: 'both' }); },
    xpan: function () { return new models.PanTool({ dimensions: 'width' }); },
    ypan: function () { return new models.PanTool({ dimensions: 'height' }); },
    xwheel_pan: function () { return new models.WheelPanTool({ dimension: "width" }); },
    ywheel_pan: function () { return new models.WheelPanTool({ dimension: "height" }); },
    wheel_zoom: function () { return new models.WheelZoomTool({ dimensions: 'both' }); },
    xwheel_zoom: function () { return new models.WheelZoomTool({ dimensions: 'width' }); },
    ywheel_zoom: function () { return new models.WheelZoomTool({ dimensions: 'height' }); },
    zoom_in: function () { return new models.ZoomInTool({ dimensions: 'both' }); },
    xzoom_in: function () { return new models.ZoomInTool({ dimensions: 'width' }); },
    yzoom_in: function () { return new models.ZoomInTool({ dimensions: 'height' }); },
    zoom_out: function () { return new models.ZoomOutTool({ dimensions: 'both' }); },
    xzoom_out: function () { return new models.ZoomOutTool({ dimensions: 'width' }); },
    yzoom_out: function () { return new models.ZoomOutTool({ dimensions: 'height' }); },
    click: function () { return new models.TapTool({ behavior: "inspect" }); },
    tap: function () { return new models.TapTool(); },
    crosshair: function () { return new models.CrosshairTool(); },
    box_select: function () { return new models.BoxSelectTool(); },
    xbox_select: function () { return new models.BoxSelectTool({ dimensions: 'width' }); },
    ybox_select: function () { return new models.BoxSelectTool({ dimensions: 'height' }); },
    poly_select: function () { return new models.PolySelectTool(); },
    lasso_select: function () { return new models.LassoSelectTool(); },
    box_zoom: function () { return new models.BoxZoomTool({ dimensions: 'both' }); },
    xbox_zoom: function () { return new models.BoxZoomTool({ dimensions: 'width' }); },
    ybox_zoom: function () { return new models.BoxZoomTool({ dimensions: 'height' }); },
    hover: function () { return new models.HoverTool({ tooltips: _default_tooltips }); },
    save: function () { return new models.SaveTool(); },
    undo: function () { return new models.UndoTool(); },
    redo: function () { return new models.RedoTool(); },
    reset: function () { return new models.ResetTool(); },
    help: function () { return new models.HelpTool(); },
};
var _default_color = "#1f77b4";
var _default_alpha = 1.0;
function _with_default(value, default_value) {
    return value === undefined ? default_value : value;
}
var Figure = /** @class */ (function (_super) {
    tslib_1.__extends(Figure, _super);
    function Figure(attributes) {
        if (attributes === void 0) { attributes = {}; }
        var _this = this;
        var attrs = object_1.clone(attributes);
        var tools = _with_default(attrs.tools, _default_tools);
        delete attrs.tools;
        attrs.x_range = Figure._get_range(attrs.x_range);
        attrs.y_range = Figure._get_range(attrs.y_range);
        var x_axis_type = _with_default(attrs.x_axis_type, "auto");
        var y_axis_type = _with_default(attrs.y_axis_type, "auto");
        delete attrs.x_axis_type;
        delete attrs.y_axis_type;
        attrs.x_scale = Figure._get_scale(attrs.x_range, x_axis_type);
        attrs.y_scale = Figure._get_scale(attrs.y_range, y_axis_type);
        var x_minor_ticks = attrs.x_minor_ticks != null ? attrs.x_minor_ticks : "auto";
        var y_minor_ticks = attrs.y_minor_ticks != null ? attrs.y_minor_ticks : "auto";
        delete attrs.x_minor_ticks;
        delete attrs.y_minor_ticks;
        var x_axis_location = attrs.x_axis_location != null ? attrs.x_axis_location : "below";
        var y_axis_location = attrs.y_axis_location != null ? attrs.y_axis_location : "left";
        delete attrs.x_axis_location;
        delete attrs.y_axis_location;
        var x_axis_label = attrs.x_axis_label != null ? attrs.x_axis_label : "";
        var y_axis_label = attrs.y_axis_label != null ? attrs.y_axis_label : "";
        delete attrs.x_axis_label;
        delete attrs.y_axis_label;
        if (attrs.width !== undefined) {
            if (attrs.plot_width === undefined) {
                attrs.plot_width = attrs.width;
            }
            else {
                throw new Error("both 'width' and 'plot_width' can't be given at the same time");
            }
            delete attrs.width;
        }
        if (attrs.height !== undefined) {
            if (attrs.plot_height === undefined) {
                attrs.plot_height = attrs.height;
            }
            else {
                throw new Error("both 'height' and 'plot_height' can't be given at the same time");
            }
            delete attrs.height;
        }
        _this = _super.call(this, attrs) || this;
        _this._process_axis_and_grid(x_axis_type, x_axis_location, x_minor_ticks, x_axis_label, attrs.x_range, 0);
        _this._process_axis_and_grid(y_axis_type, y_axis_location, y_minor_ticks, y_axis_label, attrs.y_range, 1);
        _this.add_tools.apply(_this, _this._process_tools(tools));
        _this._legend = new legend_1.Legend({ plot: _this, items: [] });
        _this.add_renderers(_this._legend);
        return _this;
    }
    Object.defineProperty(Figure.prototype, "xgrid", {
        get: function () {
            return this.renderers.filter(function (r) { return r instanceof models_1.Grid && r.dimension === 0; })[0]; // TODO
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Figure.prototype, "ygrid", {
        get: function () {
            return this.renderers.filter(function (r) { return r instanceof models_1.Grid && r.dimension === 1; })[0]; // TODO
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Figure.prototype, "xaxis", {
        get: function () {
            return this.below.concat(this.above).filter(function (r) { return r instanceof models_1.Axis; })[0]; // TODO
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Figure.prototype, "yaxis", {
        get: function () {
            return this.left.concat(this.right).filter(function (r) { return r instanceof models_1.Axis; })[0]; // TODO
        },
        enumerable: true,
        configurable: true
    });
    Figure.prototype.annular_wedge = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.AnnularWedge, "x,y,inner_radius,outer_radius,start_angle,end_angle", args);
    };
    Figure.prototype.annulus = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Annulus, "x,y,inner_radius,outer_radius", args);
    };
    Figure.prototype.arc = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Arc, "x,y,radius,start_angle,end_angle", args);
    };
    Figure.prototype.bezier = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Bezier, "x0,y0,x1,y1,cx0,cy0,cx1,cy1", args);
    };
    Figure.prototype.circle = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Circle, "x,y", args);
    };
    Figure.prototype.ellipse = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Ellipse, "x,y,width,height", args);
    };
    Figure.prototype.image = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Image, "color_mapper,image,rows,cols,x,y,dw,dh", args);
    };
    Figure.prototype.image_rgba = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.ImageRGBA, "image,rows,cols,x,y,dw,dh", args);
    };
    Figure.prototype.image_url = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.ImageURL, "url,x,y,w,h", args);
    };
    Figure.prototype.line = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Line, "x,y", args);
    };
    Figure.prototype.multi_line = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.MultiLine, "xs,ys", args);
    };
    Figure.prototype.oval = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Oval, "x,y,width,height", args);
    };
    Figure.prototype.patch = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Patch, "x,y", args);
    };
    Figure.prototype.patches = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Patches, "xs,ys", args);
    };
    Figure.prototype.quad = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Quad, "left,right,bottom,top", args);
    };
    Figure.prototype.quadratic = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Quadratic, "x0,y0,x1,y1,cx,cy", args);
    };
    Figure.prototype.ray = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Ray, "x,y,length", args);
    };
    Figure.prototype.rect = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Rect, "x,y,width,height", args);
    };
    Figure.prototype.segment = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Segment, "x0,y0,x1,y1", args);
    };
    Figure.prototype.text = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Text, "x,y,text", args);
    };
    Figure.prototype.wedge = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._glyph(models.Wedge, "x,y,radius,start_angle,end_angle", args);
    };
    Figure.prototype.asterisk = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.Asterisk, args);
    };
    Figure.prototype.circle_cross = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.CircleCross, args);
    };
    Figure.prototype.circle_x = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.CircleX, args);
    };
    Figure.prototype.cross = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.Cross, args);
    };
    Figure.prototype.dash = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.Dash, args);
    };
    Figure.prototype.diamond = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.Diamond, args);
    };
    Figure.prototype.diamond_cross = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.DiamondCross, args);
    };
    Figure.prototype.inverted_triangle = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.InvertedTriangle, args);
    };
    Figure.prototype.square = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.Square, args);
    };
    Figure.prototype.square_cross = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.SquareCross, args);
    };
    Figure.prototype.square_x = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.SquareX, args);
    };
    Figure.prototype.triangle = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.Triangle, args);
    };
    Figure.prototype.x = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return this._marker(models.X, args);
    };
    Figure.prototype._pop_colors_and_alpha = function (cls, attrs, prefix, default_color, default_alpha) {
        if (prefix === void 0) { prefix = ""; }
        if (default_color === void 0) { default_color = _default_color; }
        if (default_alpha === void 0) { default_alpha = _default_alpha; }
        var result = {};
        var color = _with_default(attrs[prefix + "color"], default_color);
        var alpha = _with_default(attrs[prefix + "alpha"], default_alpha);
        delete attrs[prefix + "color"];
        delete attrs[prefix + "alpha"];
        var _update_with = function (name, default_value) {
            if (cls.prototype.props[name] != null) {
                result[name] = _with_default(attrs[prefix + name], default_value);
                delete attrs[prefix + name];
            }
        };
        _update_with("fill_color", color);
        _update_with("line_color", color);
        _update_with("text_color", "black");
        _update_with("fill_alpha", alpha);
        _update_with("line_alpha", alpha);
        _update_with("text_alpha", alpha);
        return result;
    };
    Figure.prototype._find_uniq_name = function (data, name) {
        var i = 1;
        while (true) {
            var new_name = name + "__" + i;
            if (data[new_name] != null) {
                i += 1;
            }
            else {
                return new_name;
            }
        }
    };
    Figure.prototype._fixup_values = function (cls, data, attrs) {
        for (var name_1 in attrs) {
            var value = attrs[name_1];
            var prop = cls.prototype.props[name_1];
            if (prop != null) {
                if (prop.type.prototype.dataspec) {
                    if (value != null) {
                        if (types_1.isArray(value)) {
                            var field = void 0;
                            if (data[name_1] != null) {
                                if (data[name_1] !== value) {
                                    field = this._find_uniq_name(data, name_1);
                                    data[field] = value;
                                }
                                else {
                                    field = name_1;
                                }
                            }
                            else {
                                field = name_1;
                                data[field] = value;
                            }
                            attrs[name_1] = { field: field };
                        }
                        else if (types_1.isNumber(value) || types_1.isString(value)) { // or Date?
                            attrs[name_1] = { value: value };
                        }
                    }
                }
            }
        }
    };
    Figure.prototype._glyph = function (cls, params_string, args) {
        var params = params_string.split(",");
        var attrs;
        if (args.length === 1) {
            attrs = args[0];
            attrs = object_1.clone(attrs);
        }
        else {
            attrs = object_1.clone(args[args.length - 1]);
            for (var i = 0; i < params.length; i++) {
                var param = params[i];
                attrs[param] = args[i];
            }
        }
        var legend = this._process_legend(attrs.legend, attrs.source);
        delete attrs.legend;
        var has_sglyph = array_1.any(Object.keys(attrs), function (key) { return string_1.startsWith(key, "selection_"); });
        var has_hglyph = array_1.any(Object.keys(attrs), function (key) { return string_1.startsWith(key, "hover_"); });
        var glyph_ca = this._pop_colors_and_alpha(cls, attrs);
        var nsglyph_ca = this._pop_colors_and_alpha(cls, attrs, "nonselection_", undefined, 0.1);
        var sglyph_ca = has_sglyph ? this._pop_colors_and_alpha(cls, attrs, "selection_") : {};
        var hglyph_ca = has_hglyph ? this._pop_colors_and_alpha(cls, attrs, "hover_") : {};
        var source = attrs.source != null ? attrs.source : new models.ColumnDataSource();
        var data = object_1.clone(source.data);
        delete attrs.source;
        this._fixup_values(cls, data, glyph_ca);
        this._fixup_values(cls, data, nsglyph_ca);
        this._fixup_values(cls, data, sglyph_ca);
        this._fixup_values(cls, data, hglyph_ca);
        this._fixup_values(cls, data, attrs);
        source.data = data;
        var _make_glyph = function (cls, attrs, extra_attrs) {
            return new cls(tslib_1.__assign({}, attrs, extra_attrs));
        };
        var glyph = _make_glyph(cls, attrs, glyph_ca);
        var nsglyph = _make_glyph(cls, attrs, nsglyph_ca);
        var sglyph = has_sglyph ? _make_glyph(cls, attrs, sglyph_ca) : undefined;
        var hglyph = has_hglyph ? _make_glyph(cls, attrs, hglyph_ca) : undefined;
        var glyph_renderer = new models_1.GlyphRenderer({
            data_source: source,
            glyph: glyph,
            nonselection_glyph: nsglyph,
            selection_glyph: sglyph,
            hover_glyph: hglyph,
        });
        if (legend != null) {
            this._update_legend(legend, glyph_renderer);
        }
        this.add_renderers(glyph_renderer);
        return glyph_renderer;
    };
    Figure.prototype._marker = function (cls, args) {
        return this._glyph(cls, "x,y", args);
    };
    Figure._get_range = function (range) {
        if (range == null) {
            return new models.DataRange1d();
        }
        if (range instanceof models.Range) {
            return range;
        }
        if (types_1.isArray(range)) {
            if (array_1.all(range, types_1.isString)) {
                var factors = range;
                return new models.FactorRange({ factors: factors });
            }
            if (range.length == 2) {
                var _a = range, start = _a[0], end = _a[1];
                return new models.Range1d({ start: start, end: end });
            }
        }
        throw new Error("unable to determine proper range for: '" + range + "'");
    };
    Figure._get_scale = function (range_input, axis_type) {
        if (range_input instanceof models.DataRange1d ||
            range_input instanceof models.Range1d) {
            switch (axis_type) {
                case null:
                case "auto":
                case "linear":
                case "datetime":
                    return new models.LinearScale();
                case "log":
                    return new models.LogScale();
            }
        }
        if (range_input instanceof models.FactorRange) {
            return new models.CategoricalScale();
        }
        throw new Error("unable to determine proper scale for: '" + range_input + "'");
    };
    Figure.prototype._process_axis_and_grid = function (axis_type, axis_location, minor_ticks, axis_label, rng, dim) {
        var axiscls = this._get_axis_class(axis_type, rng);
        if (axiscls != null) {
            if (axiscls === models.LogAxis) {
                if (dim === 0) {
                    this.x_scale = new models.LogScale();
                }
                else {
                    this.y_scale = new models.LogScale();
                }
            }
            var axis = new axiscls();
            if (axis.ticker instanceof models.ContinuousTicker) {
                axis.ticker.num_minor_ticks = this._get_num_minor_ticks(axiscls, minor_ticks);
            }
            if (axis_label.length !== 0) {
                axis.axis_label = axis_label;
            }
            var grid = new models.Grid({ dimension: dim, ticker: axis.ticker });
            if (axis_location !== null) {
                this.add_layout(axis, axis_location);
            }
            this.add_layout(grid);
        }
    };
    Figure.prototype._get_axis_class = function (axis_type, range) {
        switch (axis_type) {
            case null:
                return null;
            case "linear":
                return models.LinearAxis;
            case "log":
                return models.LogAxis;
            case "datetime":
                return models.DatetimeAxis;
            case "auto":
                if (range instanceof models.FactorRange)
                    return models.CategoricalAxis;
                else
                    return models.LinearAxis; // TODO: return models.DatetimeAxis (Date type)
            default:
                throw new Error("shouldn't have happened");
        }
    };
    Figure.prototype._get_num_minor_ticks = function (axis_class, num_minor_ticks) {
        if (types_1.isNumber(num_minor_ticks)) {
            if (num_minor_ticks <= 1) {
                throw new Error("num_minor_ticks must be > 1");
            }
            return num_minor_ticks;
        }
        if (num_minor_ticks == null) {
            return 0;
        }
        if (num_minor_ticks === 'auto') {
            if (axis_class === models.LogAxis) {
                return 10;
            }
            return 5;
        }
        throw new Error("shouldn't have happened");
    };
    Figure.prototype._process_tools = function (tools) {
        if (types_1.isString(tools))
            tools = tools.split(/\s*,\s*/).filter(function (tool) { return tool.length > 0; });
        function isToolName(tool) {
            return _known_tools.hasOwnProperty(tool);
        }
        var objs = (function () {
            var result = [];
            for (var _i = 0, tools_1 = tools; _i < tools_1.length; _i++) {
                var tool = tools_1[_i];
                if (types_1.isString(tool)) {
                    if (isToolName(tool))
                        result.push(_known_tools[tool]());
                    else
                        throw new Error("unknown tool type: " + tool);
                }
                else
                    result.push(tool);
            }
            return result;
        })();
        return objs;
    };
    Figure.prototype._process_legend = function (legend, source) {
        var legend_item_label = null;
        if (legend != null) {
            if (types_1.isString(legend)) {
                legend_item_label = { value: legend };
                if ((source != null) && (source.columns() != null)) {
                    if (array_1.includes(source.columns(), legend)) {
                        legend_item_label = { field: legend };
                    }
                }
            }
            else {
                legend_item_label = legend;
            }
        }
        return legend_item_label;
    };
    Figure.prototype._update_legend = function (legend_item_label, glyph_renderer) {
        var added = false;
        for (var _i = 0, _a = this._legend.items; _i < _a.length; _i++) {
            var item = _a[_i];
            if (item.label != null && eq_1.isEqual(item.label, legend_item_label)) {
                // XXX: remove this when vectorable properties are refined
                var label = item.label;
                if ("value" in label) {
                    item.renderers.push(glyph_renderer);
                    added = true;
                    break;
                }
                if ("field" in label && glyph_renderer.data_source == item.renderers[0].data_source) {
                    item.renderers.push(glyph_renderer);
                    added = true;
                    break;
                }
            }
        }
        if (!added) {
            var new_item = new models.LegendItem({ label: legend_item_label, renderers: [glyph_renderer] });
            this._legend.items.push(new_item);
        }
    };
    return Figure;
}(models_1.Plot));
exports.Figure = Figure;
function figure(attributes) {
    if (attributes === void 0) { attributes = {}; }
    return new Figure(attributes);
}
exports.figure = figure;
exports.show = function (obj, target) {
    var doc = new document_1.Document();
    for (var _i = 0, _a = types_1.isArray(obj) ? obj : [obj]; _i < _a.length; _i++) {
        var item = _a[_i];
        doc.add_root(item);
    }
    var element;
    if (target == null) {
        element = document.body;
    }
    else if (types_1.isString(target)) {
        var found = document.querySelector(target);
        if (found != null && found instanceof HTMLElement)
            element = found;
        else
            throw new Error("'" + target + "' selector didn't match any elements");
    }
    else if (target instanceof HTMLElement) {
        element = target;
    }
    else if (typeof $ !== 'undefined' && target instanceof $) {
        element = target[0];
    }
    else {
        throw new Error("target should be HTMLElement, string selector, $ or null");
    }
    var root = dom_1.div({ class: embed_1.BOKEH_ROOT });
    element.appendChild(root);
    return embed.add_document_standalone(doc, root);
};
function color(r, g, b) {
    return sprintf_js_1.sprintf("#%02x%02x%02x", r, g, b);
}
exports.color = color;
