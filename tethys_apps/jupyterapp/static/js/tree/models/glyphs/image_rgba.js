"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var p = require("core/properties");
var array_1 = require("core/util/array");
var ImageRGBAView = /** @class */ (function (_super) {
    tslib_1.__extends(ImageRGBAView, _super);
    function ImageRGBAView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ImageRGBAView.prototype.initialize = function (options) {
        var _this = this;
        _super.prototype.initialize.call(this, options);
        this.connect(this.model.properties.global_alpha.change, function () { return _this.renderer.request_render(); });
    };
    ImageRGBAView.prototype._set_data = function (indices) {
        if (this.image_data == null || this.image_data.length != this._image.length)
            this.image_data = new Array(this._image.length);
        if (this._width == null || this._width.length != this._image.length)
            this._width = new Array(this._image.length);
        if (this._height == null || this._height.length != this._image.length)
            this._height = new Array(this._image.length);
        for (var i = 0, end = this._image.length; i < end; i++) {
            if (indices != null && indices.indexOf(i) < 0)
                continue;
            var buf = void 0;
            if (this._image_shape != null && this._image_shape[i].length > 0) {
                buf = this._image[i].buffer;
                var shape = this._image_shape[i];
                this._height[i] = shape[0];
                this._width[i] = shape[1];
            }
            else {
                var _image = this._image[i];
                var flat = array_1.concat(_image);
                buf = new ArrayBuffer(flat.length * 4);
                var color = new Uint32Array(buf);
                for (var j = 0, endj = flat.length; j < endj; j++) {
                    color[j] = flat[j];
                }
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
            var buf8 = new Uint8Array(buf);
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
    ImageRGBAView.prototype._map_data = function () {
        switch (this.model.properties.dw.units) {
            case "data": {
                this.sw = this.sdist(this.renderer.xscale, this._x, this._dw, "edge", this.model.dilate);
                break;
            }
            case "screen": {
                this.sw = this._dw;
                break;
            }
        }
        switch (this.model.properties.dh.units) {
            case "data": {
                this.sh = this.sdist(this.renderer.yscale, this._y, this._dh, "edge", this.model.dilate);
                break;
            }
            case "screen": {
                this.sh = this._dh;
                break;
            }
        }
    };
    ImageRGBAView.prototype._render = function (ctx, indices, _a) {
        var image_data = _a.image_data, sx = _a.sx, sy = _a.sy, sw = _a.sw, sh = _a.sh;
        var old_smoothing = ctx.getImageSmoothingEnabled();
        ctx.setImageSmoothingEnabled(false);
        ctx.globalAlpha = this.model.global_alpha;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
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
    ImageRGBAView.prototype.bounds = function () {
        var bbox = this.index.bbox;
        bbox.maxX += this.max_dw;
        bbox.maxY += this.max_dh;
        return bbox;
    };
    return ImageRGBAView;
}(xy_glyph_1.XYGlyphView));
exports.ImageRGBAView = ImageRGBAView;
var ImageRGBA = /** @class */ (function (_super) {
    tslib_1.__extends(ImageRGBA, _super);
    function ImageRGBA(attrs) {
        return _super.call(this, attrs) || this;
    }
    ImageRGBA.initClass = function () {
        this.prototype.type = 'ImageRGBA';
        this.prototype.default_view = ImageRGBAView;
        this.define({
            image: [p.NumberSpec],
            dw: [p.DistanceSpec],
            dh: [p.DistanceSpec],
            global_alpha: [p.Number, 1.0],
            dilate: [p.Bool, false],
        });
    };
    return ImageRGBA;
}(xy_glyph_1.XYGlyph));
exports.ImageRGBA = ImageRGBA;
ImageRGBA.initClass();
