"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var logging_1 = require("core/logging");
var p = require("core/properties");
var arrayable_1 = require("core/util/arrayable");
var spatial_1 = require("core/util/spatial");
exports.CanvasImage = Image;
var ImageURLView = /** @class */ (function (_super) {
    tslib_1.__extends(ImageURLView, _super);
    function ImageURLView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._images_rendered = false;
        return _this;
    }
    ImageURLView.prototype.initialize = function (options) {
        var _this = this;
        _super.prototype.initialize.call(this, options);
        this.connect(this.model.properties.global_alpha.change, function () { return _this.renderer.request_render(); });
    };
    ImageURLView.prototype._index_data = function () {
        return new spatial_1.SpatialIndex([]);
    };
    ImageURLView.prototype._set_data = function () {
        var _this = this;
        if (this.image == null || this.image.length != this._url.length)
            this.image = arrayable_1.map(this._url, function () { return null; });
        var _a = this.model, retry_attempts = _a.retry_attempts, retry_timeout = _a.retry_timeout;
        this.retries = arrayable_1.map(this._url, function () { return retry_attempts; });
        var _loop_1 = function (i, end) {
            if (this_1._url[i] == null)
                return "continue";
            var img = new exports.CanvasImage();
            img.onerror = function () {
                if (_this.retries[i] > 0) {
                    logging_1.logger.trace("ImageURL failed to load " + _this._url[i] + " image, retrying in " + retry_timeout + " ms");
                    setTimeout(function () { return img.src = _this._url[i]; }, retry_timeout);
                }
                else
                    logging_1.logger.warn("ImageURL unable to load " + _this._url[i] + " image after " + retry_attempts + " retries");
                _this.retries[i] -= 1;
            };
            img.onload = function () {
                _this.image[i] = img;
                _this.renderer.request_render();
            };
            img.src = this_1._url[i];
        };
        var this_1 = this;
        for (var i = 0, end = this._url.length; i < end; i++) {
            _loop_1(i, end);
        }
        var w_data = this.model.properties.w.units == "data";
        var h_data = this.model.properties.h.units == "data";
        var n = this._x.length;
        var xs = new Array(w_data ? 2 * n : n);
        var ys = new Array(h_data ? 2 * n : n);
        for (var i = 0; i < n; i++) {
            xs[i] = this._x[i];
            ys[i] = this._y[i];
        }
        // if the width/height are in screen units, don't try to include them in bounds
        if (w_data) {
            for (var i = 0; i < n; i++)
                xs[n + i] = this._x[i] + this._w[i];
        }
        if (h_data) {
            for (var i = 0; i < n; i++)
                ys[n + i] = this._y[i] + this._h[i];
        }
        var minX = arrayable_1.min(xs);
        var maxX = arrayable_1.max(xs);
        var minY = arrayable_1.min(ys);
        var maxY = arrayable_1.max(ys);
        this._bounds_rect = { minX: minX, maxX: maxX, minY: minY, maxY: maxY };
    };
    ImageURLView.prototype.has_finished = function () {
        return _super.prototype.has_finished.call(this) && this._images_rendered == true;
    };
    ImageURLView.prototype._map_data = function () {
        // Better to check this.model.w and this.model.h for null since the set_data
        // machinery will have converted this._w and this._w to lists of null
        var ws = this.model.w != null ? this._w : arrayable_1.map(this._x, function () { return NaN; });
        var hs = this.model.h != null ? this._h : arrayable_1.map(this._x, function () { return NaN; });
        switch (this.model.properties.w.units) {
            case "data": {
                this.sw = this.sdist(this.renderer.xscale, this._x, ws, "edge", this.model.dilate);
                break;
            }
            case "screen": {
                this.sw = ws;
                break;
            }
        }
        switch (this.model.properties.h.units) {
            case "data": {
                this.sh = this.sdist(this.renderer.yscale, this._y, hs, "edge", this.model.dilate);
                break;
            }
            case "screen": {
                this.sh = hs;
                break;
            }
        }
    };
    ImageURLView.prototype._render = function (ctx, indices, _a) {
        var image = _a.image, sx = _a.sx, sy = _a.sy, sw = _a.sw, sh = _a.sh, _angle = _a._angle;
        // TODO (bev): take actual border width into account when clipping
        var frame = this.renderer.plot_view.frame;
        ctx.rect(frame._left.value + 1, frame._top.value + 1, frame._width.value - 2, frame._height.value - 2);
        ctx.clip();
        var finished = true;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + _angle[i]))
                continue;
            if (this.retries[i] == -1)
                continue;
            var img = image[i];
            if (img == null) {
                finished = false;
                continue;
            }
            this._render_image(ctx, i, img, sx, sy, sw, sh, _angle);
        }
        if (finished && !this._images_rendered) {
            this._images_rendered = true;
            this.notify_finished();
        }
    };
    ImageURLView.prototype._final_sx_sy = function (anchor, sx, sy, sw, sh) {
        switch (anchor) {
            case 'top_left': return [sx, sy];
            case 'top_center': return [sx - (sw / 2), sy];
            case 'top_right': return [sx - sw, sy];
            case 'center_right': return [sx - sw, sy - (sh / 2)];
            case 'bottom_right': return [sx - sw, sy - sh];
            case 'bottom_center': return [sx - (sw / 2), sy - sh];
            case 'bottom_left': return [sx, sy - sh];
            case 'center_left': return [sx, sy - (sh / 2)];
            case 'center': return [sx - (sw / 2), sy - (sh / 2)];
        }
    };
    ImageURLView.prototype._render_image = function (ctx, i, image, sx, sy, sw, sh, angle) {
        if (isNaN(sw[i]))
            sw[i] = image.width;
        if (isNaN(sh[i]))
            sh[i] = image.height;
        var anchor = this.model.anchor;
        var _a = this._final_sx_sy(anchor, sx[i], sy[i], sw[i], sh[i]), sxi = _a[0], syi = _a[1];
        ctx.save();
        ctx.globalAlpha = this.model.global_alpha;
        if (angle[i]) {
            ctx.translate(sxi, syi);
            ctx.rotate(angle[i]);
            ctx.drawImage(image, 0, 0, sw[i], sh[i]);
            ctx.rotate(-angle[i]);
            ctx.translate(-sxi, -syi);
        }
        else
            ctx.drawImage(image, sxi, syi, sw[i], sh[i]);
        ctx.restore();
    };
    ImageURLView.prototype.bounds = function () {
        return this._bounds_rect;
    };
    return ImageURLView;
}(xy_glyph_1.XYGlyphView));
exports.ImageURLView = ImageURLView;
var ImageURL = /** @class */ (function (_super) {
    tslib_1.__extends(ImageURL, _super);
    function ImageURL(attrs) {
        return _super.call(this, attrs) || this;
    }
    ImageURL.initClass = function () {
        this.prototype.type = 'ImageURL';
        this.prototype.default_view = ImageURLView;
        this.define({
            url: [p.StringSpec],
            anchor: [p.Anchor, 'top_left'],
            global_alpha: [p.Number, 1.0],
            angle: [p.AngleSpec, 0],
            w: [p.DistanceSpec],
            h: [p.DistanceSpec],
            dilate: [p.Bool, false],
            retry_attempts: [p.Number, 0],
            retry_timeout: [p.Number, 0],
        });
    };
    return ImageURL;
}(xy_glyph_1.XYGlyph));
exports.ImageURL = ImageURL;
ImageURL.initClass();
