"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var hittest = require("core/hittest");
var p = require("core/properties");
var compat_1 = require("core/util/compat");
var AnnulusView = /** @class */ (function (_super) {
    tslib_1.__extends(AnnulusView, _super);
    function AnnulusView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AnnulusView.prototype._map_data = function () {
        if (this.model.properties.inner_radius.units == "data")
            this.sinner_radius = this.sdist(this.renderer.xscale, this._x, this._inner_radius);
        else
            this.sinner_radius = this._inner_radius;
        if (this.model.properties.outer_radius.units == "data")
            this.souter_radius = this.sdist(this.renderer.xscale, this._x, this._outer_radius);
        else
            this.souter_radius = this._outer_radius;
    };
    AnnulusView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sinner_radius = _a.sinner_radius, souter_radius = _a.souter_radius;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + sinner_radius[i] + souter_radius[i]))
                continue;
            // Because this visual has a whole in it, it proved "challenging"
            // for some browsers to render if drawn in one go --- i.e. it did not
            // work on IE. If we render in two parts (upper and lower part),
            // it is unambiguous what part should be filled. The line is
            // better drawn in one go though, otherwise the part where the pieces
            // meet will not be fully closed due to aa.
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                ctx.beginPath();
                if (compat_1.is_ie) {
                    // Draw two halves of the donut. Works on IE, but causes an aa line on Safari.
                    for (var _b = 0, _c = [false, true]; _b < _c.length; _b++) {
                        var clockwise = _c[_b];
                        ctx.arc(sx[i], sy[i], sinner_radius[i], 0, Math.PI, clockwise);
                        ctx.arc(sx[i], sy[i], souter_radius[i], Math.PI, 0, !clockwise);
                    }
                }
                else {
                    // Draw donut in one go. Does not work on iE.
                    ctx.arc(sx[i], sy[i], sinner_radius[i], 0, 2 * Math.PI, true);
                    ctx.arc(sx[i], sy[i], souter_radius[i], 2 * Math.PI, 0, false);
                }
                ctx.fill();
            }
            if (this.visuals.line.doit) {
                this.visuals.line.set_vectorize(ctx, i);
                ctx.beginPath();
                ctx.arc(sx[i], sy[i], sinner_radius[i], 0, 2 * Math.PI);
                ctx.moveTo(sx[i] + souter_radius[i], sy[i]);
                ctx.arc(sx[i], sy[i], souter_radius[i], 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
    };
    AnnulusView.prototype._hit_point = function (geometry) {
        var _a, _b;
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        var x0, y0;
        var x1, y1;
        if (this.model.properties.outer_radius.units == "data") {
            x0 = x - this.max_outer_radius;
            x1 = x + this.max_outer_radius;
            y0 = y - this.max_outer_radius;
            y1 = y + this.max_outer_radius;
        }
        else {
            var sx0 = sx - this.max_outer_radius;
            var sx1 = sx + this.max_outer_radius;
            _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
            var sy0 = sy - this.max_outer_radius;
            var sy1 = sy + this.max_outer_radius;
            _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        }
        var hits = [];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        for (var _i = 0, _c = this.index.indices(bbox); _i < _c.length; _i++) {
            var i = _c[_i];
            var or2 = Math.pow(this.souter_radius[i], 2);
            var ir2 = Math.pow(this.sinner_radius[i], 2);
            var _d = this.renderer.xscale.r_compute(x, this._x[i]), sx0 = _d[0], sx1 = _d[1];
            var _e = this.renderer.yscale.r_compute(y, this._y[i]), sy0 = _e[0], sy1 = _e[1];
            var dist = Math.pow(sx0 - sx1, 2) + Math.pow(sy0 - sy1, 2);
            if (dist <= or2 && dist >= ir2)
                hits.push([i, dist]);
        }
        return hittest.create_hit_test_result_from_hits(hits);
    };
    AnnulusView.prototype.draw_legend_for_index = function (ctx, _a, index) {
        var x0 = _a.x0, y0 = _a.y0, x1 = _a.x1, y1 = _a.y1;
        var len = index + 1;
        var sx = new Array(len);
        sx[index] = (x0 + x1) / 2;
        var sy = new Array(len);
        sy[index] = (y0 + y1) / 2;
        var r = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.5;
        var sinner_radius = new Array(len);
        sinner_radius[index] = r * 0.4;
        var souter_radius = new Array(len);
        souter_radius[index] = r * 0.8;
        this._render(ctx, [index], { sx: sx, sy: sy, sinner_radius: sinner_radius, souter_radius: souter_radius }); // XXX
    };
    return AnnulusView;
}(xy_glyph_1.XYGlyphView));
exports.AnnulusView = AnnulusView;
var Annulus = /** @class */ (function (_super) {
    tslib_1.__extends(Annulus, _super);
    function Annulus(attrs) {
        return _super.call(this, attrs) || this;
    }
    Annulus.initClass = function () {
        this.prototype.type = 'Annulus';
        this.prototype.default_view = AnnulusView;
        this.mixins(['line', 'fill']);
        this.define({
            inner_radius: [p.DistanceSpec],
            outer_radius: [p.DistanceSpec],
        });
    };
    return Annulus;
}(xy_glyph_1.XYGlyph));
exports.Annulus = Annulus;
Annulus.initClass();
