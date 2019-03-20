"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var image_pool_1 = require("./image_pool");
var p = require("core/properties");
var TileSource = /** @class */ (function (_super) {
    tslib_1.__extends(TileSource, _super);
    function TileSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    TileSource.initClass = function () {
        this.prototype.type = 'TileSource';
        this.define({
            url: [p.String, ''],
            tile_size: [p.Number, 256],
            max_zoom: [p.Number, 30],
            min_zoom: [p.Number, 0],
            extra_url_vars: [p.Any, {}],
            attribution: [p.String, ''],
            x_origin_offset: [p.Number],
            y_origin_offset: [p.Number],
            initial_resolution: [p.Number],
        });
    };
    TileSource.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.tiles = {};
        this.pool = new image_pool_1.ImagePool();
        this._normalize_case();
    };
    TileSource.prototype.string_lookup_replace = function (str, lookup) {
        var result_str = str;
        for (var key in lookup) {
            var value = lookup[key];
            result_str = result_str.replace("{" + key + "}", value);
        }
        return result_str;
    };
    TileSource.prototype._normalize_case = function () {
        /*
         * Note: should probably be refactored into subclasses.
         */
        var url = this.url
            .replace('{x}', '{X}')
            .replace('{y}', '{Y}')
            .replace('{z}', '{Z}')
            .replace('{q}', '{Q}')
            .replace('{xmin}', '{XMIN}')
            .replace('{ymin}', '{YMIN}')
            .replace('{xmax}', '{XMAX}')
            .replace('{ymax}', '{YMAX}');
        this.url = url;
    };
    TileSource.prototype.tile_xyz_to_key = function (x, y, z) {
        return x + ":" + y + ":" + z;
    };
    TileSource.prototype.key_to_tile_xyz = function (key) {
        var _a = key.split(':').map(function (c) { return parseInt(c); }), x = _a[0], y = _a[1], z = _a[2];
        return [x, y, z];
    };
    TileSource.prototype.sort_tiles_from_center = function (tiles, tile_extent) {
        var txmin = tile_extent[0], tymin = tile_extent[1], txmax = tile_extent[2], tymax = tile_extent[3];
        var center_x = ((txmax - txmin) / 2) + txmin;
        var center_y = ((tymax - tymin) / 2) + tymin;
        tiles.sort(function (a, b) {
            var a_distance = Math.sqrt(Math.pow(center_x - a[0], 2) + Math.pow(center_y - a[1], 2));
            var b_distance = Math.sqrt(Math.pow(center_x - b[0], 2) + Math.pow(center_y - b[1], 2));
            return a_distance - b_distance;
        });
    };
    TileSource.prototype.get_image_url = function (x, y, z) {
        var image_url = this.string_lookup_replace(this.url, this.extra_url_vars);
        return image_url.replace("{X}", x.toString())
            .replace('{Y}', y.toString())
            .replace("{Z}", z.toString());
    };
    return TileSource;
}(model_1.Model));
exports.TileSource = TileSource;
TileSource.initClass();
