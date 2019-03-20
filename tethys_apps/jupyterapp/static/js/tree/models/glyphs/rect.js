"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var center_rotatable_1 = require("./center_rotatable");
var utils_1 = require("./utils");
var hittest = require("core/hittest");
var p = require("core/properties");
var arrayable_1 = require("core/util/arrayable");
var RectView = /** @class */ (function (_super) {
    tslib_1.__extends(RectView, _super);
    function RectView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RectView.prototype._set_data = function () {
        this.max_w2 = 0;
        if (this.model.properties.width.units == "data")
            this.max_w2 = this.max_width / 2;
        this.max_h2 = 0;
        if (this.model.properties.height.units == "data")
            this.max_h2 = this.max_height / 2;
    };
    RectView.prototype._map_data = function () {
        var _a, _b;
        if (this.model.properties.width.units == "data")
            _a = this._map_dist_corner_for_data_side_length(this._x, this._width, this.renderer.xscale), this.sw = _a[0], this.sx0 = _a[1];
        else {
            this.sw = this._width;
            var n_1 = this.sx.length;
            this.sx0 = new Float64Array(n_1);
            for (var i = 0; i < n_1; i++)
                this.sx0[i] = this.sx[i] - this.sw[i] / 2;
        }
        if (this.model.properties.height.units == "data")
            _b = this._map_dist_corner_for_data_side_length(this._y, this._height, this.renderer.yscale), this.sh = _b[0], this.sy1 = _b[1];
        else {
            this.sh = this._height;
            var n_2 = this.sy.length;
            this.sy1 = new Float64Array(n_2);
            for (var i = 0; i < n_2; i++)
                this.sy1[i] = this.sy[i] - this.sh[i] / 2;
        }
        var n = this.sw.length;
        this.ssemi_diag = new Float64Array(n);
        for (var i = 0; i < n; i++)
            this.ssemi_diag[i] = Math.sqrt((this.sw[i] / 2 * this.sw[i]) / 2 + (this.sh[i] / 2 * this.sh[i]) / 2);
    };
    RectView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sx0 = _a.sx0, sy1 = _a.sy1, sw = _a.sw, sh = _a.sh, _angle = _a._angle;
        if (this.visuals.fill.doit) {
            for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
                var i = indices_1[_i];
                if (isNaN(sx[i] + sy[i] + sx0[i] + sy1[i] + sw[i] + sh[i] + _angle[i]))
                    continue;
                //no need to test the return value, we call fillRect for every glyph anyway
                this.visuals.fill.set_vectorize(ctx, i);
                if (_angle[i]) {
                    ctx.translate(sx[i], sy[i]);
                    ctx.rotate(_angle[i]);
                    ctx.fillRect(-sw[i] / 2, -sh[i] / 2, sw[i], sh[i]);
                    ctx.rotate(-_angle[i]);
                    ctx.translate(-sx[i], -sy[i]);
                }
                else
                    ctx.fillRect(sx0[i], sy1[i], sw[i], sh[i]);
            }
        }
        if (this.visuals.line.doit) {
            ctx.beginPath();
            for (var _b = 0, indices_2 = indices; _b < indices_2.length; _b++) {
                var i = indices_2[_b];
                if (isNaN(sx[i] + sy[i] + sx0[i] + sy1[i] + sw[i] + sh[i] + _angle[i]))
                    continue;
                // fillRect does not fill zero-height or -width rects, but rect(...)
                // does seem to stroke them (1px wide or tall). Explicitly ignore rects
                // with zero width or height to be consistent
                if (sw[i] == 0 || sh[i] == 0)
                    continue;
                if (_angle[i]) {
                    ctx.translate(sx[i], sy[i]);
                    ctx.rotate(_angle[i]);
                    ctx.rect(-sw[i] / 2, -sh[i] / 2, sw[i], sh[i]);
                    ctx.rotate(-_angle[i]);
                    ctx.translate(-sx[i], -sy[i]);
                }
                else
                    ctx.rect(sx0[i], sy1[i], sw[i], sh[i]);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
                ctx.beginPath();
            }
            ctx.stroke();
        }
    };
    RectView.prototype._hit_rect = function (geometry) {
        return this._hit_rect_against_index(geometry);
    };
    RectView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        var scenter_x = [];
        for (var i = 0, end = this.sx0.length; i < end; i++) {
            scenter_x.push(this.sx0[i] + this.sw[i] / 2);
        }
        var scenter_y = [];
        for (var i = 0, end = this.sy1.length; i < end; i++) {
            scenter_y.push(this.sy1[i] + this.sh[i] / 2);
        }
        var max_x2_ddist = arrayable_1.max(this._ddist(0, scenter_x, this.ssemi_diag));
        var max_y2_ddist = arrayable_1.max(this._ddist(1, scenter_y, this.ssemi_diag));
        var x0 = x - max_x2_ddist;
        var x1 = x + max_x2_ddist;
        var y0 = y - max_y2_ddist;
        var y1 = y + max_y2_ddist;
        var hits = [];
        var bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        for (var _i = 0, _a = this.index.indices(bbox); _i < _a.length; _i++) {
            var i = _a[_i];
            var height_in = void 0, width_in = void 0;
            if (this._angle[i]) {
                var s = Math.sin(-this._angle[i]);
                var c = Math.cos(-this._angle[i]);
                var px = c * (sx - this.sx[i]) - s * (sy - this.sy[i]) + this.sx[i];
                var py = s * (sx - this.sx[i]) + c * (sy - this.sy[i]) + this.sy[i];
                sx = px;
                sy = py;
                width_in = Math.abs(this.sx[i] - sx) <= this.sw[i] / 2;
                height_in = Math.abs(this.sy[i] - sy) <= this.sh[i] / 2;
            }
            else {
                width_in = (sx - this.sx0[i] <= this.sw[i]) && (sx - this.sx0[i] >= 0);
                height_in = (sy - this.sy1[i] <= this.sh[i]) && (sy - this.sy1[i] >= 0);
            }
            if (height_in && width_in)
                hits.push(i);
        }
        var result = hittest.create_empty_hit_test_result();
        result.indices = hits;
        return result;
    };
    RectView.prototype._map_dist_corner_for_data_side_length = function (coord, side_length, scale) {
        var n = coord.length;
        var pt0 = new Float64Array(n);
        var pt1 = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            pt0[i] = Number(coord[i]) - side_length[i] / 2;
            pt1[i] = Number(coord[i]) + side_length[i] / 2;
        }
        var spt0 = scale.v_compute(pt0);
        var spt1 = scale.v_compute(pt1);
        var sside_length = this.sdist(scale, pt0, side_length, 'edge', this.model.dilate);
        var spt_corner = spt0;
        for (var i = 0, end = spt0.length; i < end; i++) {
            if (spt0[i] != spt1[i]) {
                spt_corner = spt0[i] < spt1[i] ? spt0 : spt1;
                break;
            }
        }
        return [sside_length, spt_corner];
    };
    RectView.prototype._ddist = function (dim, spts, spans) {
        var scale = dim == 0 ? this.renderer.xscale : this.renderer.yscale;
        var spt0 = spts;
        var m = spt0.length;
        var spt1 = new Float64Array(m);
        for (var i = 0; i < m; i++)
            spt1[i] = spt0[i] + spans[i];
        var pt0 = scale.v_invert(spt0);
        var pt1 = scale.v_invert(spt1);
        var n = pt0.length;
        var ddist = new Float64Array(n);
        for (var i = 0; i < n; i++)
            ddist[i] = Math.abs(pt1[i] - pt0[i]);
        return ddist;
    };
    RectView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_area_legend(this.visuals, ctx, bbox, index);
    };
    RectView.prototype._bounds = function (_a) {
        var minX = _a.minX, maxX = _a.maxX, minY = _a.minY, maxY = _a.maxY;
        return {
            minX: minX - this.max_w2,
            maxX: maxX + this.max_w2,
            minY: minY - this.max_h2,
            maxY: maxY + this.max_h2,
        };
    };
    return RectView;
}(center_rotatable_1.CenterRotatableView));
exports.RectView = RectView;
var Rect = /** @class */ (function (_super) {
    tslib_1.__extends(Rect, _super);
    function Rect(attrs) {
        return _super.call(this, attrs) || this;
    }
    Rect.initClass = function () {
        this.prototype.type = 'Rect';
        this.prototype.default_view = RectView;
        this.define({
            dilate: [p.Bool, false],
        });
    };
    return Rect;
}(center_rotatable_1.CenterRotatable));
exports.Rect = Rect;
Rect.initClass();
