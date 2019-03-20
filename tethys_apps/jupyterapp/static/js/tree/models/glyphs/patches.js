"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var utils_1 = require("./utils");
var array_1 = require("core/util/array");
var arrayable_1 = require("core/util/arrayable");
var types_1 = require("core/util/types");
var hittest = require("core/hittest");
var PatchesView = /** @class */ (function (_super) {
    tslib_1.__extends(PatchesView, _super);
    function PatchesView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PatchesView.prototype._build_discontinuous_object = function (nanned_qs) {
        // _s is this.xs, this.ys, this.sxs, this.sys
        // an object of n 1-d arrays in either data or screen units
        //
        // Each 1-d array gets broken to an array of arrays split
        // on any NaNs
        //
        // So:
        // { 0: [x11, x12],
        //   1: [x21, x22, x23],
        //   2: [x31, NaN, x32]
        // }
        // becomes
        // { 0: [[x11, x12]],
        //   1: [[x21, x22, x23]],
        //   2: [[x31],[x32]]
        // }
        var ds = [];
        for (var i = 0, end = nanned_qs.length; i < end; i++) {
            ds[i] = [];
            var qs = array_1.copy(nanned_qs[i]);
            while (qs.length > 0) {
                var nan_index = array_1.findLastIndex(qs, function (q) { return types_1.isStrictNaN(q); });
                var qs_part = void 0;
                if (nan_index >= 0)
                    qs_part = qs.splice(nan_index);
                else {
                    qs_part = qs;
                    qs = [];
                }
                var denanned = qs_part.filter(function (q) { return !types_1.isStrictNaN(q); });
                ds[i].push(denanned);
            }
        }
        return ds;
    };
    PatchesView.prototype._index_data = function () {
        var xss = this._build_discontinuous_object(this._xs); // XXX
        var yss = this._build_discontinuous_object(this._ys); // XXX
        var points = [];
        for (var i = 0, end = this._xs.length; i < end; i++) {
            for (var j = 0, endj = xss[i].length; j < endj; j++) {
                var xs = xss[i][j];
                var ys = yss[i][j];
                if (xs.length == 0)
                    continue;
                points.push({
                    minX: array_1.min(xs),
                    minY: array_1.min(ys),
                    maxX: array_1.max(xs),
                    maxY: array_1.max(ys),
                    i: i,
                });
            }
        }
        return new spatial_1.SpatialIndex(points);
    };
    PatchesView.prototype._mask_data = function () {
        var xr = this.renderer.plot_view.frame.x_ranges["default"];
        var _a = [xr.min, xr.max], x0 = _a[0], x1 = _a[1];
        var yr = this.renderer.plot_view.frame.y_ranges["default"];
        var _b = [yr.min, yr.max], y0 = _b[0], y1 = _b[1];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var indices = this.index.indices(bbox);
        // TODO (bev) this should be under test
        return indices.sort(function (a, b) { return a - b; });
    };
    PatchesView.prototype._render = function (ctx, indices, _a) {
        var sxs = _a.sxs, sys = _a.sys;
        // this.sxss and this.syss are used by _hit_point and sxc, syc
        // This is the earliest we can build them, and only build them once
        this.sxss = this._build_discontinuous_object(sxs); // XXX
        this.syss = this._build_discontinuous_object(sys); // XXX
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            var _b = [sxs[i], sys[i]], sx = _b[0], sy = _b[1];
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                for (var j = 0, end = sx.length; j < end; j++) {
                    if (j == 0) {
                        ctx.beginPath();
                        ctx.moveTo(sx[j], sy[j]);
                        continue;
                    }
                    else if (isNaN(sx[j] + sy[j])) {
                        ctx.closePath();
                        ctx.fill();
                        ctx.beginPath();
                        continue;
                    }
                    else
                        ctx.lineTo(sx[j], sy[j]);
                }
                ctx.closePath();
                ctx.fill();
            }
            if (this.visuals.line.doit) {
                this.visuals.line.set_vectorize(ctx, i);
                for (var j = 0, end = sx.length; j < end; j++) {
                    if (j == 0) {
                        ctx.beginPath();
                        ctx.moveTo(sx[j], sy[j]);
                        continue;
                    }
                    else if (isNaN(sx[j] + sy[j])) {
                        ctx.closePath();
                        ctx.stroke();
                        ctx.beginPath();
                        continue;
                    }
                    else
                        ctx.lineTo(sx[j], sy[j]);
                }
                ctx.closePath();
                ctx.stroke();
            }
        }
    };
    PatchesView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        var candidates = this.index.indices({ minX: x, minY: y, maxX: x, maxY: y });
        var hits = [];
        for (var i = 0, end = candidates.length; i < end; i++) {
            var idx = candidates[i];
            var sxs = this.sxss[idx];
            var sys = this.syss[idx];
            for (var j = 0, endj = sxs.length; j < endj; j++) {
                if (hittest.point_in_poly(sx, sy, sxs[j], sys[j])) {
                    hits.push(idx);
                }
            }
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    PatchesView.prototype._get_snap_coord = function (array) {
        return arrayable_1.sum(array) / array.length;
    };
    PatchesView.prototype.scenterx = function (i, sx, sy) {
        if (this.sxss[i].length == 1) {
            // We don't have discontinuous objects so we're ok
            return this._get_snap_coord(this.sxs[i]);
        }
        else {
            // We have discontinuous objects, so we need to find which
            // one we're in, we can use point_in_poly again
            var sxs = this.sxss[i];
            var sys = this.syss[i];
            for (var j = 0, end = sxs.length; j < end; j++) {
                if (hittest.point_in_poly(sx, sy, sxs[j], sys[j]))
                    return this._get_snap_coord(sxs[j]);
            }
        }
        throw new Error("unreachable code");
    };
    PatchesView.prototype.scentery = function (i, sx, sy) {
        if (this.syss[i].length == 1) {
            // We don't have discontinuous objects so we're ok
            return this._get_snap_coord(this.sys[i]);
        }
        else {
            // We have discontinuous objects, so we need to find which
            // one we're in, we can use point_in_poly again
            var sxs = this.sxss[i];
            var sys = this.syss[i];
            for (var j = 0, end = sxs.length; j < end; j++) {
                if (hittest.point_in_poly(sx, sy, sxs[j], sys[j]))
                    return this._get_snap_coord(sys[j]);
            }
        }
        throw new Error("unreachable code");
    };
    PatchesView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    return PatchesView;
}(glyph_1.GlyphView));
exports.PatchesView = PatchesView;
var Patches = /** @class */ (function (_super) {
    tslib_1.__extends(Patches, _super);
    function Patches(attrs) {
        return _super.call(this, attrs) || this;
    }
    Patches.initClass = function () {
        this.prototype.type = 'Patches';
        this.prototype.default_view = PatchesView;
        this.coords([['xs', 'ys']]);
        this.mixins(['line', 'fill']);
    };
    return Patches;
}(glyph_1.Glyph));
exports.Patches = Patches;
Patches.initClass();
