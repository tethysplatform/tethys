"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var linear_color_mapper_1 = require("../mappers/linear_color_mapper");
var p = require("core/properties");
var array_1 = require("core/util/array");
var spatial_1 = require("core/util/spatial");
var hittest = require("core/hittest");
var ImageView = /** @class */ (function (_super) {
    tslib_1.__extends(ImageView, _super);
    function ImageView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ImageView.prototype.initialize = function (options) {
        var _this = this;
        _super.prototype.initialize.call(this, options);
        this.connect(this.model.color_mapper.change, function () { return _this._update_image(); });
        this.connect(this.model.properties.global_alpha.change, function () { return _this.renderer.request_render(); });
    };
    ImageView.prototype._update_image = function () {
        // Only reset image_data if already initialized
        if (this.image_data != null) {
            this._set_data();
            this.renderer.plot_view.request_render();
        }
    };
    ImageView.prototype._index_data = function () {
        var points = [];
        for (var i = 0, end = this._x.length; i < end; i++) {
            var _a = this._lrtb(i), l = _a[0], r = _a[1], t = _a[2], b = _a[3];
            if (isNaN(l + r + t + b) || !isFinite(l + r + t + b)) {
                continue;
            }
            points.push({ minX: l, minY: b, maxX: r, maxY: t, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    ImageView.prototype._lrtb = function (i) {
        var xr = this.renderer.xscale.source_range;
        var x1 = this._x[i];
        var x2 = xr.is_reversed ? x1 - this._dw[i] : x1 + this._dw[i];
        var yr = this.renderer.yscale.source_range;
        var y1 = this._y[i];
        var y2 = yr.is_reversed ? y1 - this._dh[i] : y1 + this._dh[i];
        var _a = x1 < x2 ? [x1, x2] : [x2, x1], l = _a[0], r = _a[1];
        var _b = y1 < y2 ? [y1, y2] : [y2, y1], b = _b[0], t = _b[1];
        return [l, r, t, b];
    };
    ImageView.prototype._image_index = function (index, x, y) {
        var _a = this._lrtb(index), l = _a[0], r = _a[1], t = _a[2], b = _a[3];
        var width = this._width[index];
        var height = this._height[index];
        var dx = (r - l) / width;
        var dy = (t - b) / height;
        var dim1 = Math.floor((x - l) / dx);
        var dim2 = Math.floor((y - b) / dy);
        return { index: index, dim1: dim1, dim2: dim2, flat_index: dim2 * width + dim1 };
    };
    ImageView.prototype._hit_point = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var x = this.renderer.xscale.invert(sx);
        var y = this.renderer.yscale.invert(sy);
        var bbox = hittest.validate_bbox_coords([x, x], [y, y]);
        var candidates = this.index.indices(bbox);
        var result = hittest.create_empty_hit_test_result();
        result.image_indices = [];
        for (var _i = 0, candidates_1 = candidates; _i < candidates_1.length; _i++) {
            var index = candidates_1[_i];
            if ((sx != Infinity) && (sy != Infinity)) {
                result.image_indices.push(this._image_index(index, x, y));
            }
        }
        return result;
    };
    ImageView.prototype._set_data = function () {
        if (this.image_data == null || this.image_data.length != this._image.length)
            this.image_data = new Array(this._image.length);
        if (this._width == null || this._width.length != this._image.length)
            this._width = new Array(this._image.length);
        if (this._height == null || this._height.length != this._image.length)
            this._height = new Array(this._image.length);
        var cmap = this.model.color_mapper.rgba_mapper;
        for (var i = 0, end = this._image.length; i < end; i++) {
            var img = void 0;
            if (this._image_shape != null && this._image_shape[i].length > 0) {
                img = this._image[i];
                var shape = this._image_shape[i];
                this._height[i] = shape[0];
                this._width[i] = shape[1];
            }
            else {
                var _image = this._image[i];
                img = array_1.concat(_image);
                this._height[i] = _image.length;
                this._width[i] = _image[0].length;
            }
            var _image_data = this.image_data[i];
            var canvas = void 0;
            if (_image_data != null && _image_data.width == this._width[i] &&
                _image_data.height == this._height[i])
                canvas = _image_data;
            else {
                canvas = document.createElement('canvas');
                canvas.width = this._width[i];
                canvas.height = this._height[i];
            }
            var ctx = canvas.getContext('2d');
            var image_data = ctx.getImageData(0, 0, this._width[i], this._height[i]);
            var buf8 = cmap.v_compute(img);
            image_data.data.set(buf8);
            ctx.putImageData(image_data, 0, 0);
            this.image_data[i] = canvas;
            this.max_dw = 0;
            if (this.model.properties.dw.units == "data")
                this.max_dw = array_1.max(this._dw);
            this.max_dh = 0;
            if (this.model.properties.dh.units == "data")
                this.max_dh = array_1.max(this._dh);
        }
    };
    ImageView.prototype._map_data = function () {
        switch (this.model.properties.dw.units) {
            case "data": {
                this.sw = this.sdist(this.renderer.xscale, this._x, this._dw, 'edge', this.model.dilate);
                break;
            }
            case "screen": {
                this.sw = this._dw;
                break;
            }
        }
        switch (this.model.properties.dh.units) {
            case "data": {
                this.sh = this.sdist(this.renderer.yscale, this._y, this._dh, 'edge', this.model.dilate);
                break;
            }
            case "screen": {
                this.sh = this._dh;
                break;
            }
        }
    };
    ImageView.prototype._render = function (ctx, indices, _a) {
        var image_data = _a.image_data, sx = _a.sx, sy = _a.sy, sw = _a.sw, sh = _a.sh;
        var old_smoothing = ctx.getImageSmoothingEnabled();
        ctx.setImageSmoothingEnabled(false);
        ctx.globalAlpha = this.model.global_alpha;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (image_data[i] == null)
                continue;
            if (isNaN(sx[i] + sy[i] + sw[i] + sh[i]))
                continue;
            var y_offset = sy[i];
            ctx.translate(0, y_offset);
            ctx.scale(1, -1);
            ctx.translate(0, -y_offset);
            ctx.drawImage(image_data[i], sx[i] | 0, sy[i] | 0, sw[i], sh[i]);
            ctx.translate(0, y_offset);
            ctx.scale(1, -1);
            ctx.translate(0, -y_offset);
        }
        ctx.setImageSmoothingEnabled(old_smoothing);
    };
    ImageView.prototype.bounds = function () {
        var bbox = this.index.bbox;
        bbox.maxX += this.max_dw;
        bbox.maxY += this.max_dh;
        return bbox;
    };
    return ImageView;
}(xy_glyph_1.XYGlyphView));
exports.ImageView = ImageView;
// NOTE: this needs to be redefined here, because palettes are located in bokeh-api.js bundle
var Greys9 = function () { return ["#000000", "#252525", "#525252", "#737373", "#969696", "#bdbdbd", "#d9d9d9", "#f0f0f0", "#ffffff"]; };
var Image = /** @class */ (function (_super) {
    tslib_1.__extends(Image, _super);
    function Image(attrs) {
        return _super.call(this, attrs) || this;
    }
    Image.initClass = function () {
        this.prototype.type = 'Image';
        this.prototype.default_view = ImageView;
        this.define({
            image: [p.NumberSpec],
            dw: [p.DistanceSpec],
            dh: [p.DistanceSpec],
            dilate: [p.Bool, false],
            global_alpha: [p.Number, 1.0],
            color_mapper: [p.Instance, function () { return new linear_color_mapper_1.LinearColorMapper({ palette: Greys9() }); }],
        });
    };
    return Image;
}(xy_glyph_1.XYGlyph));
exports.Image = Image;
Image.initClass();
