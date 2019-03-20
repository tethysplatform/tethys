"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var glyph_1 = require("./glyph");
var hittest = require("core/hittest");
var p = require("core/properties");
var spatial_1 = require("core/util/spatial");
var utils_1 = require("./utils");
var HexTileView = /** @class */ (function (_super) {
    tslib_1.__extends(HexTileView, _super);
    function HexTileView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    HexTileView.prototype.scenterx = function (i) { return this.sx[i]; };
    HexTileView.prototype.scentery = function (i) { return this.sy[i]; };
    HexTileView.prototype._set_data = function () {
        var n = this._q.length;
        var size = this.model.size;
        var aspect_scale = this.model.aspect_scale;
        this._x = new Float64Array(n);
        this._y = new Float64Array(n);
        if (this.model.orientation == "pointytop") {
            for (var i = 0; i < n; i++) {
                this._x[i] = size * Math.sqrt(3) * (this._q[i] + this._r[i] / 2) / aspect_scale;
                this._y[i] = -size * 3 / 2 * this._r[i];
            }
        }
        else {
            for (var i = 0; i < n; i++) {
                this._x[i] = size * 3 / 2 * this._q[i];
                this._y[i] = -size * Math.sqrt(3) * (this._r[i] + this._q[i] / 2) * aspect_scale;
            }
        }
    };
    HexTileView.prototype._index_data = function () {
        var _a;
        var ysize = this.model.size;
        var xsize = Math.sqrt(3) * ysize / 2;
        if (this.model.orientation == "flattop") {
            _a = [ysize, xsize], xsize = _a[0], ysize = _a[1];
            ysize *= this.model.aspect_scale;
        }
        else {
            xsize /= this.model.aspect_scale;
        }
        var points = [];
        for (var i = 0; i < this._x.length; i++) {
            var x = this._x[i];
            var y = this._y[i];
            if (isNaN(x + y) || !isFinite(x + y))
                continue;
            points.push({ minX: x - xsize, minY: y - ysize, maxX: x + xsize, maxY: y + ysize, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    // overriding map_data instead of _map_data because the default automatic mappings
    // for other glyphs (with cartesian coordinates) is not useful
    HexTileView.prototype.map_data = function () {
        var _a, _b;
        _a = this.map_to_screen(this._x, this._y), this.sx = _a[0], this.sy = _a[1];
        _b = this._get_unscaled_vertices(), this.svx = _b[0], this.svy = _b[1];
    };
    HexTileView.prototype._get_unscaled_vertices = function () {
        var size = this.model.size;
        var aspect_scale = this.model.aspect_scale;
        if (this.model.orientation == "pointytop") {
            var rscale = this.renderer.yscale;
            var hscale = this.renderer.xscale;
            var r = Math.abs(rscale.compute(0) - rscale.compute(size)); // assumes linear scale
            var h = Math.sqrt(3) / 2 * Math.abs(hscale.compute(0) - hscale.compute(size)) / aspect_scale; // assumes linear scale
            var r2 = r / 2.0;
            var svx = [0, -h, -h, 0, h, h];
            var svy = [r, r2, -r2, -r, -r2, r2];
            return [svx, svy];
        }
        else {
            var rscale = this.renderer.xscale;
            var hscale = this.renderer.yscale;
            var r = Math.abs(rscale.compute(0) - rscale.compute(size)); // assumes linear scale
            var h = Math.sqrt(3) / 2 * Math.abs(hscale.compute(0) - hscale.compute(size)) * aspect_scale; // assumes linear scale
            var r2 = r / 2.0;
            var svx = [r, r2, -r2, -r, -r2, r2];
            var svy = [0, -h, -h, 0, h, h];
            return [svx, svy];
        }
    };
    HexTileView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, svx = _a.svx, svy = _a.svy, _scale = _a._scale;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + _scale[i]))
                continue;
            ctx.translate(sx[i], sy[i]);
            ctx.beginPath();
            for (var j = 0; j < 6; j++) {
                ctx.lineTo(svx[j] * _scale[i], svy[j] * _scale[i]);
            }
            ctx.closePath();
            ctx.translate(-sx[i], -sy[i]);
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                ctx.fill();
            }
            if (this.visuals.line.doit) {
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    HexTileView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        var candidates = this.index.indices({ minX: x, minY: y, maxX: x, maxY: y });
        var hits = [];
        for (var _i = 0, candidates_1 = candidates; _i < candidates_1.length; _i++) {
            var i = candidates_1[_i];
            if (hittest.point_in_poly(sx - this.sx[i], sy - this.sy[i], this.svx, this.svy)) {
                hits.push(i);
            }
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    HexTileView.prototype._hit_span = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var hits;
        if (geometry.direction == 'v') {
            var y = this.renderer.yscale.invert(sy);
            var hr = this.renderer.plot_view.frame.bbox.h_range;
            var _a = this.renderer.xscale.r_invert(hr.start, hr.end), minX = _a[0], maxX = _a[1];
            hits = this.index.indices({ minX: minX, minY: y, maxX: maxX, maxY: y });
        }
        else {
            var x = this.renderer.xscale.invert(sx);
            var vr = this.renderer.plot_view.frame.bbox.v_range;
            var _b = this.renderer.yscale.r_invert(vr.start, vr.end), minY = _b[0], maxY = _b[1];
            hits = this.index.indices({ minX: x, minY: minY, maxX: x, maxY: maxY });
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    HexTileView.prototype._hit_rect = function (geometry) {
        var sx0 = geometry.sx0, sx1 = geometry.sx1, sy0 = geometry.sy0, sy1 = geometry.sy1;
        var _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var result = hittest.create_empty_hit_test_result();
        result.indices = this.index.indices(bbox);
        return result;
    };
    HexTileView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    return HexTileView;
}(glyph_1.GlyphView));
exports.HexTileView = HexTileView;
var HexTile = /** @class */ (function (_super) {
    tslib_1.__extends(HexTile, _super);
    function HexTile(attrs) {
        return _super.call(this, attrs) || this;
    }
    HexTile.initClass = function () {
        this.prototype.type = 'HexTile';
        this.prototype.default_view = HexTileView;
        this.coords([['r', 'q']]);
        this.mixins(['line', 'fill']);
        this.define({
            size: [p.Number, 1.0],
            aspect_scale: [p.Number, 1.0],
            scale: [p.NumberSpec, 1.0],
            orientation: [p.String, "pointytop"],
        });
        this.override({ line_color: null });
    };
    return HexTile;
}(glyph_1.Glyph));
exports.HexTile = HexTile;
HexTile.initClass();
