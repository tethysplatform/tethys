"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var hittest = require("core/hittest");
var p = require("core/properties");
var text_1 = require("core/util/text");
var TextView = /** @class */ (function (_super) {
    tslib_1.__extends(TextView, _super);
    function TextView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TextView.prototype._rotate_point = function (x, y, xoff, yoff, angle) {
        var sxr = (x - xoff) * Math.cos(angle) - (y - yoff) * Math.sin(angle) + xoff;
        var syr = (x - xoff) * Math.sin(angle) + (y - yoff) * Math.cos(angle) + yoff;
        return [sxr, syr];
    };
    TextView.prototype._text_bounds = function (x0, y0, width, height) {
        var xvals = [x0, x0 + width, x0 + width, x0, x0];
        var yvals = [y0, y0, y0 - height, y0 - height, y0];
        return [xvals, yvals];
    };
    TextView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, _x_offset = _a._x_offset, _y_offset = _a._y_offset, _angle = _a._angle, _text = _a._text;
        this._sys = [];
        this._sxs = [];
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + _x_offset[i] + _y_offset[i] + _angle[i]) || _text[i] == null)
                continue;
            this._sxs[i] = [];
            this._sys[i] = [];
            if (this.visuals.text.doit) {
                var text = "" + _text[i];
                ctx.save();
                ctx.translate(sx[i] + _x_offset[i], sy[i] + _y_offset[i]);
                ctx.rotate(_angle[i]);
                this.visuals.text.set_vectorize(ctx, i);
                var font = this.visuals.text.cache_select("font", i);
                var height = text_1.get_text_height(font).height;
                var line_height = this.visuals.text.text_line_height.value() * height;
                if (text.indexOf("\n") == -1) {
                    ctx.fillText(text, 0, 0);
                    var x0 = sx[i] + _x_offset[i];
                    var y0 = sy[i] + _y_offset[i];
                    var width = ctx.measureText(text).width;
                    var _b = this._text_bounds(x0, y0, width, line_height), xvalues = _b[0], yvalues = _b[1];
                    this._sxs[i].push(xvalues);
                    this._sys[i].push(yvalues);
                }
                else {
                    var lines = text.split("\n");
                    var block_height = line_height * lines.length;
                    var baseline = this.visuals.text.cache_select("text_baseline", i);
                    var y = void 0;
                    switch (baseline) {
                        case "top": {
                            y = 0;
                            break;
                        }
                        case "middle": {
                            y = (-block_height / 2) + (line_height / 2);
                            break;
                        }
                        case "bottom": {
                            y = -block_height + line_height;
                            break;
                        }
                        default: {
                            y = 0;
                            console.warn("'" + baseline + "' baseline not supported with multi line text");
                        }
                    }
                    for (var _c = 0, lines_1 = lines; _c < lines_1.length; _c++) {
                        var line = lines_1[_c];
                        ctx.fillText(line, 0, y);
                        var x0 = sx[i] + _x_offset[i];
                        var y0 = y + sy[i] + _y_offset[i];
                        var width = ctx.measureText(line).width;
                        var _d = this._text_bounds(x0, y0, width, line_height), xvalues = _d[0], yvalues = _d[1];
                        this._sxs[i].push(xvalues);
                        this._sys[i].push(yvalues);
                        y += line_height;
                    }
                }
                ctx.restore();
            }
        }
    };
    TextView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var hits = [];
        for (var i = 0; i < this._sxs.length; i++) {
            var sxs = this._sxs[i];
            var sys = this._sys[i];
            var n = sxs.length;
            for (var j = 0, endj = n; j < endj; j++) {
                var _a = this._rotate_point(sx, sy, sxs[n - 1][0], sys[n - 1][0], -this._angle[i]), sxr = _a[0], syr = _a[1];
                if (hittest.point_in_poly(sxr, syr, sxs[j], sys[j])) {
                    hits.push(i);
                }
            }
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    TextView.prototype._scenterxy = function (i) {
        var sx0 = this._sxs[i][0][0];
        var sy0 = this._sys[i][0][0];
        var sxc = (this._sxs[i][0][2] + sx0) / 2;
        var syc = (this._sys[i][0][2] + sy0) / 2;
        var _a = this._rotate_point(sxc, syc, sx0, sy0, this._angle[i]), sxcr = _a[0], sycr = _a[1];
        return { x: sxcr, y: sycr };
    };
    TextView.prototype.scenterx = function (i) {
        return this._scenterxy(i).x;
    };
    TextView.prototype.scentery = function (i) {
        return this._scenterxy(i).y;
    };
    return TextView;
}(xy_glyph_1.XYGlyphView));
exports.TextView = TextView;
var Text = /** @class */ (function (_super) {
    tslib_1.__extends(Text, _super);
    function Text(attrs) {
        return _super.call(this, attrs) || this;
    }
    Text.initClass = function () {
        this.prototype.type = 'Text';
        this.prototype.default_view = TextView;
        this.mixins(['text']);
        this.define({
            text: [p.StringSpec, { field: "text" }],
            angle: [p.AngleSpec, 0],
            x_offset: [p.NumberSpec, 0],
            y_offset: [p.NumberSpec, 0],
        });
    };
    return Text;
}(xy_glyph_1.XYGlyph));
exports.Text = Text;
Text.initClass();
