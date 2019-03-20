"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var hittest = require("core/hittest");
var p = require("core/properties");
var bbox = require("core/util/bbox");
var proj = require("core/util/projections");
var visuals = require("core/visuals");
var view_1 = require("core/view");
var model_1 = require("../../model");
var logging_1 = require("core/logging");
var arrayable_1 = require("core/util/arrayable");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
var line_1 = require("./line");
var factor_range_1 = require("../ranges/factor_range");
var GlyphView = /** @class */ (function (_super) {
    tslib_1.__extends(GlyphView, _super);
    function GlyphView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._nohit_warned = {};
        return _this;
    }
    GlyphView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this._nohit_warned = {};
        this.renderer = options.renderer;
        this.visuals = new visuals.Visuals(this.model);
        // Init gl (this should really be done anytime renderer is set,
        // and not done if it isn't ever set, but for now it only
        // matters in the unit tests because we build a view without a
        // renderer there)
        var gl = this.renderer.plot_view.gl;
        if (gl != null) {
            var webgl_module = null;
            try {
                webgl_module = require("./webgl/index");
            }
            catch (e) {
                if (e.code === 'MODULE_NOT_FOUND') {
                    logging_1.logger.warn('WebGL was requested and is supported, but bokeh-gl(.min).js is not available, falling back to 2D rendering.');
                }
                else
                    throw e;
            }
            if (webgl_module != null) {
                var Cls = webgl_module[this.model.type + 'GLGlyph'];
                if (Cls != null)
                    this.glglyph = new Cls(gl.ctx, this);
            }
        }
    };
    GlyphView.prototype.set_visuals = function (source) {
        this.visuals.warm_cache(source);
        if (this.glglyph != null)
            this.glglyph.set_visuals_changed();
    };
    GlyphView.prototype.render = function (ctx, indices, data) {
        ctx.beginPath();
        if (this.glglyph != null) {
            if (this.glglyph.render(ctx, indices, data))
                return;
        }
        this._render(ctx, indices, data);
    };
    GlyphView.prototype.has_finished = function () {
        return true;
    };
    GlyphView.prototype.notify_finished = function () {
        this.renderer.notify_finished();
    };
    GlyphView.prototype._bounds = function (bounds) {
        return bounds;
    };
    GlyphView.prototype.bounds = function () {
        return this._bounds(this.index.bbox);
    };
    GlyphView.prototype.log_bounds = function () {
        var bb = bbox.empty();
        var positive_x_bbs = this.index.search(bbox.positive_x());
        for (var _i = 0, positive_x_bbs_1 = positive_x_bbs; _i < positive_x_bbs_1.length; _i++) {
            var x = positive_x_bbs_1[_i];
            if (x.minX < bb.minX)
                bb.minX = x.minX;
            if (x.maxX > bb.maxX)
                bb.maxX = x.maxX;
        }
        var positive_y_bbs = this.index.search(bbox.positive_y());
        for (var _a = 0, positive_y_bbs_1 = positive_y_bbs; _a < positive_y_bbs_1.length; _a++) {
            var y = positive_y_bbs_1[_a];
            if (y.minY < bb.minY)
                bb.minY = y.minY;
            if (y.maxY > bb.maxY)
                bb.maxY = y.maxY;
        }
        return this._bounds(bb);
    };
    GlyphView.prototype.get_anchor_point = function (anchor, i, _a) {
        var sx = _a[0], sy = _a[1];
        switch (anchor) {
            case "center": return { x: this.scenterx(i, sx, sy), y: this.scentery(i, sx, sy) };
            default: return null;
        }
    };
    GlyphView.prototype.sdist = function (scale, pts, spans, pts_location, dilate) {
        if (pts_location === void 0) { pts_location = "edge"; }
        if (dilate === void 0) { dilate = false; }
        var pt0;
        var pt1;
        var n = pts.length;
        if (pts_location == 'center') {
            var halfspan = arrayable_1.map(spans, function (d) { return d / 2; });
            pt0 = new Float64Array(n);
            for (var i = 0; i < n; i++) {
                pt0[i] = pts[i] - halfspan[i];
            }
            pt1 = new Float64Array(n);
            for (var i = 0; i < n; i++) {
                pt1[i] = pts[i] + halfspan[i];
            }
        }
        else {
            pt0 = pts;
            pt1 = new Float64Array(n);
            for (var i = 0; i < n; i++) {
                pt1[i] = pt0[i] + spans[i];
            }
        }
        var spt0 = scale.v_compute(pt0);
        var spt1 = scale.v_compute(pt1);
        if (dilate)
            return arrayable_1.map(spt0, function (_, i) { return Math.ceil(Math.abs(spt1[i] - spt0[i])); });
        else
            return arrayable_1.map(spt0, function (_, i) { return Math.abs(spt1[i] - spt0[i]); });
    };
    GlyphView.prototype.draw_legend_for_index = function (_ctx, _bbox, _index) { };
    GlyphView.prototype.hit_test = function (geometry) {
        var result = null;
        var func = "_hit_" + geometry.type;
        if (this[func] != null) {
            result = this[func](geometry);
        }
        else if (this._nohit_warned[geometry.type] == null) {
            logging_1.logger.debug("'" + geometry.type + "' selection not available for " + this.model.type);
            this._nohit_warned[geometry.type] = true;
        }
        return result;
    };
    GlyphView.prototype._hit_rect_against_index = function (geometry) {
        var sx0 = geometry.sx0, sx1 = geometry.sx1, sy0 = geometry.sy0, sy1 = geometry.sy1;
        var _a = this.renderer.xscale.r_invert(sx0, sx1), x0 = _a[0], x1 = _a[1];
        var _b = this.renderer.yscale.r_invert(sy0, sy1), y0 = _b[0], y1 = _b[1];
        var bb = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
        var result = hittest.create_empty_hit_test_result();
        result.indices = this.index.indices(bb);
        return result;
    };
    GlyphView.prototype.set_data = function (source, indices, indices_to_update) {
        var _a, _b, _c, _d;
        var data = this.model.materialize_dataspecs(source);
        this.visuals.set_all_indices(indices);
        if (indices && !(this instanceof line_1.LineView)) {
            var data_subset = {};
            var _loop_1 = function (k) {
                var v = data[k];
                if (k.charAt(0) === '_')
                    data_subset[k] = indices.map(function (i) { return v[i]; });
                else
                    data_subset[k] = v;
            };
            for (var k in data) {
                _loop_1(k);
            }
            data = data_subset;
        }
        var self = this;
        object_1.extend(self, data);
        // TODO (bev) Should really probably delegate computing projected
        // coordinates to glyphs, instead of centralizing here in one place.
        if (this.renderer.plot_view.model.use_map) {
            if (self._x != null)
                _a = proj.project_xy(self._x, self._y), self._x = _a[0], self._y = _a[1];
            if (self._xs != null)
                _b = proj.project_xsys(self._xs, self._ys), self._xs = _b[0], self._ys = _b[1];
            if (self._x0 != null)
                _c = proj.project_xy(self._x0, self._y0), self._x0 = _c[0], self._y0 = _c[1];
            if (self._x1 != null)
                _d = proj.project_xy(self._x1, self._y1), self._x1 = _d[0], self._y1 = _d[1];
        }
        // if we have any coordinates that are categorical, convert them to
        // synthetic coords here
        if (this.renderer.plot_view.frame.x_ranges != null) { // XXXX JUST TEMP FOR TESTS TO PASS
            var xr_1 = this.renderer.plot_view.frame.x_ranges[this.model.x_range_name];
            var yr_1 = this.renderer.plot_view.frame.y_ranges[this.model.y_range_name];
            for (var _i = 0, _e = this.model._coords; _i < _e.length; _i++) {
                var _f = _e[_i], xname = _f[0], yname = _f[1];
                xname = "_" + xname;
                yname = "_" + yname;
                // TODO (bev) more robust detection of multi-glyph case
                // hand multi glyph case
                if (self._xs != null) {
                    if (xr_1 instanceof factor_range_1.FactorRange) {
                        self[xname] = arrayable_1.map(self[xname], function (arr) { return xr_1.v_synthetic(arr); });
                    }
                    if (yr_1 instanceof factor_range_1.FactorRange) {
                        self[yname] = arrayable_1.map(self[yname], function (arr) { return yr_1.v_synthetic(arr); });
                    }
                }
                // hand standard glyph case
                else {
                    if (xr_1 instanceof factor_range_1.FactorRange) {
                        self[xname] = xr_1.v_synthetic(self[xname]);
                    }
                    if (yr_1 instanceof factor_range_1.FactorRange) {
                        self[yname] = yr_1.v_synthetic(self[yname]);
                    }
                }
            }
        }
        if (this.glglyph != null)
            this.glglyph.set_data_changed(self._x.length);
        this._set_data(indices_to_update); //TODO doesn't take subset indices into account
        this.index_data();
    };
    GlyphView.prototype._set_data = function (_indices) { };
    GlyphView.prototype.index_data = function () {
        this.index = this._index_data();
    };
    GlyphView.prototype.mask_data = function (indices) {
        // WebGL can do the clipping much more efficiently
        if (this.glglyph != null || this._mask_data == null)
            return indices;
        else
            return this._mask_data();
    };
    GlyphView.prototype.map_data = function () {
        var _a;
        // TODO: if using gl, skip this (when is this called?)
        // map all the coordinate fields
        var self = this;
        for (var _i = 0, _b = this.model._coords; _i < _b.length; _i++) {
            var _c = _b[_i], xname = _c[0], yname = _c[1];
            var sxname = "s" + xname;
            var syname = "s" + yname;
            xname = "_" + xname;
            yname = "_" + yname;
            if (self[xname] != null && (types_1.isArray(self[xname][0]) || types_1.isTypedArray(self[xname][0]))) {
                var n = self[xname].length;
                self[sxname] = new Array(n);
                self[syname] = new Array(n);
                for (var i = 0; i < n; i++) {
                    var _d = this.map_to_screen(self[xname][i], self[yname][i]), sx = _d[0], sy = _d[1];
                    self[sxname][i] = sx;
                    self[syname][i] = sy;
                }
            }
            else
                _a = this.map_to_screen(self[xname], self[yname]), self[sxname] = _a[0], self[syname] = _a[1];
        }
        this._map_data();
    };
    // This is where specs not included in coords are computed, e.g. radius.
    GlyphView.prototype._map_data = function () { };
    GlyphView.prototype.map_to_screen = function (x, y) {
        return this.renderer.plot_view.map_to_screen(x, y, this.model.x_range_name, this.model.y_range_name);
    };
    return GlyphView;
}(view_1.View));
exports.GlyphView = GlyphView;
var Glyph = /** @class */ (function (_super) {
    tslib_1.__extends(Glyph, _super);
    function Glyph(attrs) {
        return _super.call(this, attrs) || this;
    }
    Glyph.initClass = function () {
        this.prototype.type = 'Glyph';
        this.prototype._coords = [];
        this.internal({
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
    };
    Glyph.coords = function (coords) {
        var _coords = this.prototype._coords.concat(coords);
        this.prototype._coords = _coords;
        var result = {};
        for (var _i = 0, coords_1 = coords; _i < coords_1.length; _i++) {
            var _a = coords_1[_i], x = _a[0], y = _a[1];
            result[x] = [p.NumberSpec];
            result[y] = [p.NumberSpec];
        }
        this.define(result);
    };
    return Glyph;
}(model_1.Model));
exports.Glyph = Glyph;
Glyph.initClass();
