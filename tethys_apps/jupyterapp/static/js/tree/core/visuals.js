"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var mixins = require("./property_mixins");
var color_1 = require("./util/color");
var ContextProperties = /** @class */ (function () {
    function ContextProperties(obj, prefix) {
        if (prefix === void 0) { prefix = ""; }
        this.obj = obj;
        this.prefix = prefix;
        // }
        this.cache = {};
        var do_spec = obj.properties[prefix + this.do_attr].spec;
        this.doit = do_spec.value !== null; // XXX: can't be `undefined`, see TODOs below.
        for (var _i = 0, _a = this.attrs; _i < _a.length; _i++) {
            var attr = _a[_i];
            this[attr] = obj.properties[prefix + attr];
        }
    }
    ContextProperties.prototype.warm_cache = function (source) {
        for (var _i = 0, _a = this.attrs; _i < _a.length; _i++) {
            var attr = _a[_i];
            var prop = this.obj.properties[this.prefix + attr];
            if (prop.spec.value !== undefined) // TODO (bev) better test?
                this.cache[attr] = prop.spec.value;
            else if (source != null)
                this.cache[attr + "_array"] = prop.array(source);
            else
                throw new Error("source is required with a vectorized visual property");
        }
    };
    ContextProperties.prototype.cache_select = function (attr, i) {
        var prop = this.obj.properties[this.prefix + attr];
        var value;
        if (prop.spec.value !== undefined) // TODO (bev) better test?
            this.cache[attr] = value = prop.spec.value;
        else
            this.cache[attr] = value = this.cache[attr + "_array"][i];
        return value;
    };
    ContextProperties.prototype.set_vectorize = function (ctx, i) {
        if (this.all_indices != null) // all_indices is set by a Visuals instance associated with a CDSView
            this._set_vectorize(ctx, this.all_indices[i]);
        else // all_indices is not set for annotations which may have vectorized visual props
            this._set_vectorize(ctx, i);
    };
    return ContextProperties;
}());
exports.ContextProperties = ContextProperties;
var Line = /** @class */ (function (_super) {
    tslib_1.__extends(Line, _super);
    function Line() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Line.prototype.set_value = function (ctx) {
        ctx.strokeStyle = this.line_color.value();
        ctx.globalAlpha = this.line_alpha.value();
        ctx.lineWidth = this.line_width.value();
        ctx.lineJoin = this.line_join.value();
        ctx.lineCap = this.line_cap.value();
        ctx.setLineDash(this.line_dash.value());
        ctx.setLineDashOffset(this.line_dash_offset.value());
    };
    Line.prototype._set_vectorize = function (ctx, i) {
        this.cache_select("line_color", i);
        if (ctx.strokeStyle !== this.cache.line_color)
            ctx.strokeStyle = this.cache.line_color;
        this.cache_select("line_alpha", i);
        if (ctx.globalAlpha !== this.cache.line_alpha)
            ctx.globalAlpha = this.cache.line_alpha;
        this.cache_select("line_width", i);
        if (ctx.lineWidth !== this.cache.line_width)
            ctx.lineWidth = this.cache.line_width;
        this.cache_select("line_join", i);
        if (ctx.lineJoin !== this.cache.line_join)
            ctx.lineJoin = this.cache.line_join;
        this.cache_select("line_cap", i);
        if (ctx.lineCap !== this.cache.line_cap)
            ctx.lineCap = this.cache.line_cap;
        this.cache_select("line_dash", i);
        if (ctx.getLineDash() !== this.cache.line_dash)
            ctx.setLineDash(this.cache.line_dash);
        this.cache_select("line_dash_offset", i);
        if (ctx.getLineDashOffset() !== this.cache.line_dash_offset)
            ctx.setLineDashOffset(this.cache.line_dash_offset);
    };
    Line.prototype.color_value = function () {
        var _a = color_1.color2rgba(this.line_color.value(), this.line_alpha.value()), r = _a[0], g = _a[1], b = _a[2], a = _a[3];
        return "rgba(" + r * 255 + "," + g * 255 + "," + b * 255 + "," + a + ")";
    };
    return Line;
}(ContextProperties));
exports.Line = Line;
Line.prototype.attrs = Object.keys(mixins.line());
Line.prototype.do_attr = "line_color";
var Fill = /** @class */ (function (_super) {
    tslib_1.__extends(Fill, _super);
    function Fill() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Fill.prototype.set_value = function (ctx) {
        ctx.fillStyle = this.fill_color.value();
        ctx.globalAlpha = this.fill_alpha.value();
    };
    Fill.prototype._set_vectorize = function (ctx, i) {
        this.cache_select("fill_color", i);
        if (ctx.fillStyle !== this.cache.fill_color)
            ctx.fillStyle = this.cache.fill_color;
        this.cache_select("fill_alpha", i);
        if (ctx.globalAlpha !== this.cache.fill_alpha)
            ctx.globalAlpha = this.cache.fill_alpha;
    };
    Fill.prototype.color_value = function () {
        var _a = color_1.color2rgba(this.fill_color.value(), this.fill_alpha.value()), r = _a[0], g = _a[1], b = _a[2], a = _a[3];
        return "rgba(" + r * 255 + "," + g * 255 + "," + b * 255 + "," + a + ")";
    };
    return Fill;
}(ContextProperties));
exports.Fill = Fill;
Fill.prototype.attrs = Object.keys(mixins.fill());
Fill.prototype.do_attr = "fill_color";
var Text = /** @class */ (function (_super) {
    tslib_1.__extends(Text, _super);
    function Text() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Text.prototype.cache_select = function (name, i) {
        var value;
        if (name == "font") {
            _super.prototype.cache_select.call(this, "text_font_style", i);
            _super.prototype.cache_select.call(this, "text_font_size", i);
            _super.prototype.cache_select.call(this, "text_font", i);
            var _a = this.cache, text_font_style = _a.text_font_style, text_font_size = _a.text_font_size, text_font = _a.text_font;
            this.cache.font = value = text_font_style + " " + text_font_size + " " + text_font;
        }
        else
            value = _super.prototype.cache_select.call(this, name, i);
        return value;
    };
    Text.prototype.font_value = function () {
        var font = this.text_font.value();
        var font_size = this.text_font_size.value();
        var font_style = this.text_font_style.value();
        return font_style + " " + font_size + " " + font;
    };
    Text.prototype.color_value = function () {
        var _a = color_1.color2rgba(this.text_color.value(), this.text_alpha.value()), r = _a[0], g = _a[1], b = _a[2], a = _a[3];
        return "rgba(" + r * 255 + "," + g * 255 + "," + b * 255 + "," + a + ")";
    };
    Text.prototype.set_value = function (ctx) {
        ctx.font = this.font_value();
        ctx.fillStyle = this.text_color.value();
        ctx.globalAlpha = this.text_alpha.value();
        ctx.textAlign = this.text_align.value();
        ctx.textBaseline = this.text_baseline.value();
    };
    Text.prototype._set_vectorize = function (ctx, i) {
        this.cache_select("font", i);
        if (ctx.font !== this.cache.font)
            ctx.font = this.cache.font;
        this.cache_select("text_color", i);
        if (ctx.fillStyle !== this.cache.text_color)
            ctx.fillStyle = this.cache.text_color;
        this.cache_select("text_alpha", i);
        if (ctx.globalAlpha !== this.cache.text_alpha)
            ctx.globalAlpha = this.cache.text_alpha;
        this.cache_select("text_align", i);
        if (ctx.textAlign !== this.cache.text_align)
            ctx.textAlign = this.cache.text_align;
        this.cache_select("text_baseline", i);
        if (ctx.textBaseline !== this.cache.text_baseline)
            ctx.textBaseline = this.cache.text_baseline;
    };
    return Text;
}(ContextProperties));
exports.Text = Text;
Text.prototype.attrs = Object.keys(mixins.text());
Text.prototype.do_attr = "text_color";
var Visuals = /** @class */ (function () {
    function Visuals(model) {
        for (var _i = 0, _a = model.mixins; _i < _a.length; _i++) {
            var spec = _a[_i];
            var _b = spec.split(":"), name_1 = _b[0], _c = _b[1], prefix = _c === void 0 ? "" : _c;
            var cls = void 0;
            switch (name_1) {
                case "line":
                    cls = Line;
                    break;
                case "fill":
                    cls = Fill;
                    break;
                case "text":
                    cls = Text;
                    break;
                default:
                    throw new Error("unknown visual: " + name_1);
            }
            this[prefix + name_1] = new cls(model, prefix);
        }
    }
    Visuals.prototype.warm_cache = function (source) {
        for (var name_2 in this) {
            if (this.hasOwnProperty(name_2)) {
                var prop = this[name_2];
                if (prop instanceof ContextProperties)
                    prop.warm_cache(source);
            }
        }
    };
    Visuals.prototype.set_all_indices = function (all_indices) {
        for (var name_3 in this) {
            if (this.hasOwnProperty(name_3)) {
                var prop = this[name_3];
                if (prop instanceof ContextProperties)
                    prop.all_indices = all_indices;
            }
        }
    };
    return Visuals;
}());
exports.Visuals = Visuals;
