"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var image_pool_1 = require("./image_pool");
var wmts_tile_source_1 = require("./wmts_tile_source");
var renderer_1 = require("../renderers/renderer");
var range1d_1 = require("../ranges/range1d");
var dom_1 = require("core/dom");
var p = require("core/properties");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var TileRendererView = /** @class */ (function (_super) {
    tslib_1.__extends(TileRendererView, _super);
    function TileRendererView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TileRendererView.prototype.initialize = function (options) {
        this.attributionEl = null;
        this._tiles = [];
        _super.prototype.initialize.call(this, options);
    };
    TileRendererView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.request_render(); });
    };
    TileRendererView.prototype.get_extent = function () {
        return [this.x_range.start, this.y_range.start, this.x_range.end, this.y_range.end];
    };
    Object.defineProperty(TileRendererView.prototype, "map_plot", {
        get: function () {
            return this.plot_model.plot;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(TileRendererView.prototype, "map_canvas", {
        get: function () {
            return this.plot_view.canvas_view.ctx;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(TileRendererView.prototype, "map_frame", {
        get: function () {
            return this.plot_model.frame;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(TileRendererView.prototype, "x_range", {
        get: function () {
            return this.map_plot.x_range;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(TileRendererView.prototype, "y_range", {
        get: function () {
            return this.map_plot.y_range;
        },
        enumerable: true,
        configurable: true
    });
    TileRendererView.prototype._set_data = function () {
        this.pool = new image_pool_1.ImagePool();
        this.extent = this.get_extent();
        this._last_height = undefined;
        this._last_width = undefined;
    };
    TileRendererView.prototype._add_attribution = function () {
        var attribution = this.model.tile_source.attribution;
        if (types_1.isString(attribution) && attribution.length > 0) {
            if (this.attributionEl == null) {
                var right = this.plot_model.canvas._right.value - this.plot_model.frame._right.value;
                var bottom = this.plot_model.canvas._bottom.value - this.plot_model.frame._bottom.value;
                var max_width = this.map_frame._width.value;
                this.attributionEl = dom_1.div({
                    class: 'bk-tile-attribution',
                    style: {
                        position: "absolute",
                        bottom: bottom + "px",
                        right: right + "px",
                        'max-width': max_width - 4 /*padding*/ + "px",
                        padding: "2px",
                        'background-color': 'rgba(255,255,255,0.5)',
                        'font-size': '7pt',
                        'font-family': 'sans-serif',
                        'line-height': '1.05',
                        'white-space': 'nowrap',
                        overflow: 'hidden',
                        'text-overflow': 'ellipsis',
                    },
                });
                var overlays = this.plot_view.canvas_view.events_el;
                overlays.appendChild(this.attributionEl);
            }
            this.attributionEl.innerHTML = attribution;
            this.attributionEl.title = this.attributionEl.textContent.replace(/\s*\n\s*/g, " ");
        }
    };
    TileRendererView.prototype._map_data = function () {
        this.initial_extent = this.get_extent();
        var zoom_level = this.model.tile_source.get_level_by_extent(this.initial_extent, this.map_frame._height.value, this.map_frame._width.value);
        var new_extent = this.model.tile_source.snap_to_zoom_level(this.initial_extent, this.map_frame._height.value, this.map_frame._width.value, zoom_level);
        this.x_range.start = new_extent[0];
        this.y_range.start = new_extent[1];
        this.x_range.end = new_extent[2];
        this.y_range.end = new_extent[3];
        if (this.x_range instanceof range1d_1.Range1d) {
            this.x_range.reset_start = new_extent[0];
            this.x_range.reset_end = new_extent[2];
        }
        if (this.y_range instanceof range1d_1.Range1d) {
            this.y_range.reset_start = new_extent[1];
            this.y_range.reset_end = new_extent[3];
        }
        this._add_attribution();
    };
    TileRendererView.prototype._on_tile_load = function (tile_data, e) {
        tile_data.img = e.target;
        tile_data.loaded = true;
        this.request_render();
    };
    TileRendererView.prototype._on_tile_cache_load = function (tile_data, e) {
        tile_data.img = e.target;
        tile_data.loaded = true;
        tile_data.finished = true;
        this.notify_finished();
    };
    TileRendererView.prototype._on_tile_error = function (tile_data) {
        tile_data.finished = true;
    };
    TileRendererView.prototype._create_tile = function (x, y, z, bounds, cache_only) {
        if (cache_only === void 0) { cache_only = false; }
        var _a = this.model.tile_source.normalize_xyz(x, y, z), nx = _a[0], ny = _a[1], nz = _a[2];
        var img = this.pool.pop();
        var tile = {
            img: img,
            tile_coords: [x, y, z],
            normalized_coords: [nx, ny, nz],
            quadkey: this.model.tile_source.tile_xyz_to_quadkey(x, y, z),
            cache_key: this.model.tile_source.tile_xyz_to_key(x, y, z),
            bounds: bounds,
            loaded: false,
            finished: false,
            x_coord: bounds[0],
            y_coord: bounds[3],
        };
        img.onload = cache_only ? this._on_tile_cache_load.bind(this, tile) : this._on_tile_load.bind(this, tile);
        img.onerror = this._on_tile_error.bind(this, tile);
        img.alt = '';
        img.src = this.model.tile_source.get_image_url(nx, ny, nz);
        this.model.tile_source.tiles[tile.cache_key] = tile;
        this._tiles.push(tile);
    };
    TileRendererView.prototype._enforce_aspect_ratio = function () {
        // brute force way of handling resize or sizing_mode event -------------------------------------------------------------
        if ((this._last_height !== this.map_frame._height.value) || (this._last_width !== this.map_frame._width.value)) {
            var extent = this.get_extent();
            var zoom_level = this.model.tile_source.get_level_by_extent(extent, this.map_frame._height.value, this.map_frame._width.value);
            var new_extent = this.model.tile_source.snap_to_zoom_level(extent, this.map_frame._height.value, this.map_frame._width.value, zoom_level);
            this.x_range.setv({ start: new_extent[0], end: new_extent[2] });
            this.y_range.setv({ start: new_extent[1], end: new_extent[3] });
            this.extent = new_extent;
            this._last_height = this.map_frame._height.value;
            this._last_width = this.map_frame._width.value;
        }
    };
    TileRendererView.prototype.has_finished = function () {
        if (!_super.prototype.has_finished.call(this)) {
            return false;
        }
        if (this._tiles.length === 0) {
            return false;
        }
        for (var _i = 0, _a = this._tiles; _i < _a.length; _i++) {
            var tile = _a[_i];
            if (!tile.finished) {
                return false;
            }
        }
        return true;
    };
    TileRendererView.prototype.render = function () {
        if (this.map_initialized == null) {
            this._set_data();
            this._map_data();
            this.map_initialized = true;
        }
        this._enforce_aspect_ratio();
        this._update();
        if (this.prefetch_timer != null) {
            clearTimeout(this.prefetch_timer);
        }
        this.prefetch_timer = setTimeout(this._prefetch_tiles.bind(this), 500);
        if (this.has_finished()) {
            this.notify_finished();
        }
    };
    TileRendererView.prototype._draw_tile = function (tile_key) {
        var tile_obj = this.model.tile_source.tiles[tile_key];
        if (tile_obj != null) {
            var _a = this.plot_view.map_to_screen([tile_obj.bounds[0]], [tile_obj.bounds[3]]), sxmin = _a[0][0], symin = _a[1][0]; // XXX: TS #20623
            var _b = this.plot_view.map_to_screen([tile_obj.bounds[2]], [tile_obj.bounds[1]]), sxmax = _b[0][0], symax = _b[1][0]; //
            var sw = sxmax - sxmin;
            var sh = symax - symin;
            var sx = sxmin;
            var sy = symin;
            var old_smoothing = this.map_canvas.getImageSmoothingEnabled();
            this.map_canvas.setImageSmoothingEnabled(this.model.smoothing);
            this.map_canvas.drawImage(tile_obj.img, sx, sy, sw, sh);
            this.map_canvas.setImageSmoothingEnabled(old_smoothing);
            tile_obj.finished = true;
        }
    };
    TileRendererView.prototype._set_rect = function () {
        var outline_width = this.plot_model.plot.properties.outline_line_width.value();
        var l = this.map_frame._left.value + (outline_width / 2);
        var t = this.map_frame._top.value + (outline_width / 2);
        var w = this.map_frame._width.value - outline_width;
        var h = this.map_frame._height.value - outline_width;
        this.map_canvas.rect(l, t, w, h);
        this.map_canvas.clip();
    };
    TileRendererView.prototype._render_tiles = function (tile_keys) {
        this.map_canvas.save();
        this._set_rect();
        this.map_canvas.globalAlpha = this.model.alpha;
        for (var _i = 0, tile_keys_1 = tile_keys; _i < tile_keys_1.length; _i++) {
            var tile_key = tile_keys_1[_i];
            this._draw_tile(tile_key);
        }
        this.map_canvas.restore();
    };
    TileRendererView.prototype._prefetch_tiles = function () {
        var tile_source = this.model.tile_source;
        var extent = this.get_extent();
        var h = this.map_frame._height.value;
        var w = this.map_frame._width.value;
        var zoom_level = this.model.tile_source.get_level_by_extent(extent, h, w);
        var tiles = this.model.tile_source.get_tiles_by_extent(extent, zoom_level);
        for (var t = 0, end = Math.min(10, tiles.length); t < end; t++) {
            var _a = tiles[t], x = _a[0], y = _a[1], z = _a[2];
            var children = this.model.tile_source.children_by_tile_xyz(x, y, z);
            for (var _i = 0, children_1 = children; _i < children_1.length; _i++) {
                var c = children_1[_i];
                var cx = c[0], cy = c[1], cz = c[2], cbounds = c[3];
                if (tile_source.tile_xyz_to_key(cx, cy, cz) in tile_source.tiles) {
                    continue;
                }
                else {
                    this._create_tile(cx, cy, cz, cbounds, true);
                }
            }
        }
    };
    TileRendererView.prototype._fetch_tiles = function (tiles) {
        for (var _i = 0, tiles_1 = tiles; _i < tiles_1.length; _i++) {
            var tile = tiles_1[_i];
            var x = tile[0], y = tile[1], z = tile[2], bounds = tile[3];
            this._create_tile(x, y, z, bounds);
        }
    };
    TileRendererView.prototype._update = function () {
        var _this = this;
        var tile_source = this.model.tile_source;
        var min_zoom = tile_source.min_zoom;
        var max_zoom = tile_source.max_zoom;
        var extent = this.get_extent();
        var zooming_out = (this.extent[2] - this.extent[0]) < (extent[2] - extent[0]);
        var h = this.map_frame._height.value;
        var w = this.map_frame._width.value;
        var zoom_level = tile_source.get_level_by_extent(extent, h, w);
        var snap_back = false;
        if (zoom_level < min_zoom) {
            extent = this.extent;
            zoom_level = min_zoom;
            snap_back = true;
        }
        else if (zoom_level > max_zoom) {
            extent = this.extent;
            zoom_level = max_zoom;
            snap_back = true;
        }
        if (snap_back) {
            this.x_range.setv({ x_range: { start: extent[0], end: extent[2] } });
            this.y_range.setv({ start: extent[1], end: extent[3] });
            this.extent = extent;
        }
        this.extent = extent;
        var tiles = tile_source.get_tiles_by_extent(extent, zoom_level);
        var need_load = [];
        var cached = [];
        var parents = [];
        var children = [];
        for (var _i = 0, tiles_2 = tiles; _i < tiles_2.length; _i++) {
            var t = tiles_2[_i];
            var x = t[0], y = t[1], z = t[2];
            var key = tile_source.tile_xyz_to_key(x, y, z);
            var tile = tile_source.tiles[key];
            if (tile != null && tile.loaded) {
                cached.push(key);
            }
            else {
                if (this.model.render_parents) {
                    var _a = tile_source.get_closest_parent_by_tile_xyz(x, y, z), px = _a[0], py = _a[1], pz = _a[2];
                    var parent_key = tile_source.tile_xyz_to_key(px, py, pz);
                    var parent_tile = tile_source.tiles[parent_key];
                    if ((parent_tile != null) && parent_tile.loaded && !array_1.includes(parents, parent_key)) {
                        parents.push(parent_key);
                    }
                    if (zooming_out) {
                        var child_tiles = tile_source.children_by_tile_xyz(x, y, z);
                        for (var _b = 0, child_tiles_1 = child_tiles; _b < child_tiles_1.length; _b++) {
                            var _c = child_tiles_1[_b], cx = _c[0], cy = _c[1], cz = _c[2];
                            var child_key = tile_source.tile_xyz_to_key(cx, cy, cz);
                            if (child_key in tile_source.tiles)
                                children.push(child_key);
                        }
                    }
                }
            }
            if (tile == null)
                need_load.push(t);
        }
        // draw stand-in parents ----------
        this._render_tiles(parents);
        this._render_tiles(children);
        // draw cached ----------
        this._render_tiles(cached);
        // fetch missing -------
        if (this.render_timer != null) {
            clearTimeout(this.render_timer);
        }
        this.render_timer = setTimeout((function () { return _this._fetch_tiles(need_load); }), 65);
    };
    return TileRendererView;
}(renderer_1.RendererView));
exports.TileRendererView = TileRendererView;
var TileRenderer = /** @class */ (function (_super) {
    tslib_1.__extends(TileRenderer, _super);
    function TileRenderer(attrs) {
        return _super.call(this, attrs) || this;
    }
    TileRenderer.initClass = function () {
        this.prototype.type = 'TileRenderer';
        this.prototype.default_view = TileRendererView;
        this.define({
            alpha: [p.Number, 1.0],
            x_range_name: [p.String, "default"],
            y_range_name: [p.String, "default"],
            smoothing: [p.Bool, true],
            tile_source: [p.Instance, function () { return new wmts_tile_source_1.WMTSTileSource(); }],
            render_parents: [p.Bool, true],
        });
        this.override({
            level: 'underlay',
        });
    };
    return TileRenderer;
}(renderer_1.Renderer));
exports.TileRenderer = TileRenderer;
TileRenderer.initClass();
