"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var XYGlyphView = /** @class */ (function (_super) {
    tslib_1.__extends(XYGlyphView, _super);
    function XYGlyphView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    XYGlyphView.prototype._index_data = function () {
        var points = [];
        for (var i = 0, end = this._x.length; i < end; i++) {
            var x = this._x[i];
            var y = this._y[i];
            if (isNaN(x + y) || !isFinite(x + y))
                continue;
            points.push({ minX: x, minY: y, maxX: x, maxY: y, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    XYGlyphView.prototype.scenterx = function (i) {
        return this.sx[i];
    };
    XYGlyphView.prototype.scentery = function (i) {
        return this.sy[i];
    };
    return XYGlyphView;
}(glyph_1.GlyphView));
exports.XYGlyphView = XYGlyphView;
var XYGlyph = /** @class */ (function (_super) {
    tslib_1.__extends(XYGlyph, _super);
    function XYGlyph(attrs) {
        return _super.call(this, attrs) || this;
    }
    XYGlyph.initClass = function () {
        this.prototype.type = "XYGlyph";
        this.coords([['x', 'y']]);
    };
    return XYGlyph;
}(glyph_1.Glyph));
exports.XYGlyph = XYGlyph;
XYGlyph.initClass();
