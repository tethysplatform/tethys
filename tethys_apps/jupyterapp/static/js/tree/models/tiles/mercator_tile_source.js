"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tile_source_1 = require("./tile_source");
var p = require("core/properties");
var array_1 = require("core/util/array");
var tile_utils_1 = require("./tile_utils");
var MercatorTileSource = /** @class */ (function (_super) {
    tslib_1.__extends(MercatorTileSource, _super);
    function MercatorTileSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    MercatorTileSource.initClass = function () {
        this.prototype.type = 'MercatorTileSource';
        this.define({
            snap_to_zoom: [p.Bool, false],
            wrap_around: [p.Bool, true],
        });
        this.override({
            x_origin_offset: 20037508.34,
            y_origin_offset: 20037508.34,
            initial_resolution: 156543.03392804097,
        });
    };
    MercatorTileSource.prototype.initialize = function () {
        var _this = this;
        _super.prototype.initialize.call(this);
        this._resolutions = array_1.range(this.min_zoom, this.max_zoom + 1).map(function (z) { return _this.get_resolution(z); });
    };
    MercatorTileSource.prototype._computed_initial_resolution = function () {
        if (this.initial_resolution != null)
            return this.initial_resolution;
        else {
            // TODO testing 2015-11-17, if this codepath is used it seems
            // to use 100% cpu and wedge Chrome
            return (2 * Math.PI * 6378137) / this.tile_size;
        }
    };
    MercatorTileSource.prototype.is_valid_tile = function (x, y, z) {
        if (!this.wrap_around) {
            if (x < 0 || x >= Math.pow(2, z))
                return false;
        }
        if (y < 0 || y >= Math.pow(2, z))
            return false;
        return true;
    };
    MercatorTileSource.prototype.parent_by_tile_xyz = function (x, y, z) {
        var quadkey = this.tile_xyz_to_quadkey(x, y, z);
        var parent_quadkey = quadkey.substring(0, quadkey.length - 1);
        return this.quadkey_to_tile_xyz(parent_quadkey);
    };
    MercatorTileSource.prototype.get_resolution = function (level) {
        return this._computed_initial_resolution() / Math.pow(2, level);
    };
    MercatorTileSource.prototype.get_resolution_by_extent = function (extent, height, width) {
        var x_rs = (extent[2] - extent[0]) / width;
        var y_rs = (extent[3] - extent[1]) / height;
        return [x_rs, y_rs];
    };
    MercatorTileSource.prototype.get_level_by_extent = function (extent, height, width) {
        var x_rs = (extent[2] - extent[0]) / width;
        var y_rs = (extent[3] - extent[1]) / height;
        var resolution = Math.max(x_rs, y_rs);
        var i = 0;
        for (var _i = 0, _a = this._resolutions; _i < _a.length; _i++) {
            var r = _a[_i];
            if (resolution > r) {
                if (i == 0)
                    return 0;
                if (i > 0)
                    return i - 1;
            }
            i += 1;
        }
        // otherwise return the highest available resolution
        return (i - 1);
    };
    MercatorTileSource.prototype.get_closest_level_by_extent = function (extent, height, width) {
        var x_rs = (extent[2] - extent[0]) / width;
        var y_rs = (extent[3] - extent[1]) / height;
        var resolution = Math.max(x_rs, y_rs);
        var closest = this._resolutions.reduce(function (previous, current) {
            if (Math.abs(current - resolution) < Math.abs(previous - resolution)) {
                return current;
            }
            return previous;
        });
        return this._resolutions.indexOf(closest);
    };
    MercatorTileSource.prototype.snap_to_zoom_level = function (extent, height, width, level) {
        var xmin = extent[0], ymin = extent[1], xmax = extent[2], ymax = extent[3];
        var desired_res = this._resolutions[level];
        var desired_x_delta = width * desired_res;
        var desired_y_delta = height * desired_res;
        if (!this.snap_to_zoom) {
            var xscale = (xmax - xmin) / desired_x_delta;
            var yscale = (ymax - ymin) / desired_y_delta;
            if (xscale > yscale) {
                desired_x_delta = (xmax - xmin);
                desired_y_delta = desired_y_delta * xscale;
            }
            else {
                desired_x_delta = desired_x_delta * yscale;
                desired_y_delta = (ymax - ymin);
            }
        }
        var x_adjust = (desired_x_delta - (xmax - xmin)) / 2;
        var y_adjust = (desired_y_delta - (ymax - ymin)) / 2;
        return [xmin - x_adjust, ymin - y_adjust, xmax + x_adjust, ymax + y_adjust];
    };
    MercatorTileSource.prototype.tms_to_wmts = function (x, y, z) {
        'Note this works both ways';
        return [x, Math.pow(2, z) - 1 - y, z];
    };
    MercatorTileSource.prototype.wmts_to_tms = function (x, y, z) {
        'Note this works both ways';
        return [x, Math.pow(2, z) - 1 - y, z];
    };
    MercatorTileSource.prototype.pixels_to_meters = function (px, py, level) {
        var res = this.get_resolution(level);
        var mx = (px * res) - this.x_origin_offset;
        var my = (py * res) - this.y_origin_offset;
        return [mx, my];
    };
    MercatorTileSource.prototype.meters_to_pixels = function (mx, my, level) {
        var res = this.get_resolution(level);
        var px = (mx + this.x_origin_offset) / res;
        var py = (my + this.y_origin_offset) / res;
        return [px, py];
    };
    MercatorTileSource.prototype.pixels_to_tile = function (px, py) {
        var tx = Math.ceil(px / this.tile_size);
        tx = tx === 0 ? tx : tx - 1;
        var ty = Math.max(Math.ceil(py / this.tile_size) - 1, 0);
        return [tx, ty];
    };
    MercatorTileSource.prototype.pixels_to_raster = function (px, py, level) {
        var mapSize = this.tile_size << level;
        return [px, mapSize - py];
    };
    MercatorTileSource.prototype.meters_to_tile = function (mx, my, level) {
        var _a = this.meters_to_pixels(mx, my, level), px = _a[0], py = _a[1];
        return this.pixels_to_tile(px, py);
    };
    MercatorTileSource.prototype.get_tile_meter_bounds = function (tx, ty, level) {
        // expects tms styles coordinates (bottom-left origin)
        var _a = this.pixels_to_meters(tx * this.tile_size, ty * this.tile_size, level), xmin = _a[0], ymin = _a[1];
        var _b = this.pixels_to_meters((tx + 1) * this.tile_size, (ty + 1) * this.tile_size, level), xmax = _b[0], ymax = _b[1];
        return [xmin, ymin, xmax, ymax];
    };
    MercatorTileSource.prototype.get_tile_geographic_bounds = function (tx, ty, level) {
        var bounds = this.get_tile_meter_bounds(tx, ty, level);
        var _a = tile_utils_1.meters_extent_to_geographic(bounds), minLon = _a[0], minLat = _a[1], maxLon = _a[2], maxLat = _a[3];
        return [minLon, minLat, maxLon, maxLat];
    };
    MercatorTileSource.prototype.get_tiles_by_extent = function (extent, level, tile_border) {
        if (tile_border === void 0) { tile_border = 1; }
        // unpack extent and convert to tile coordinates
        var xmin = extent[0], ymin = extent[1], xmax = extent[2], ymax = extent[3];
        var _a = this.meters_to_tile(xmin, ymin, level), txmin = _a[0], tymin = _a[1];
        var _b = this.meters_to_tile(xmax, ymax, level), txmax = _b[0], tymax = _b[1];
        // add tiles which border
        txmin -= tile_border;
        tymin -= tile_border;
        txmax += tile_border;
        tymax += tile_border;
        var tiles = [];
        for (var ty = tymax; ty >= tymin; ty--) {
            for (var tx = txmin; tx <= txmax; tx++) {
                if (this.is_valid_tile(tx, ty, level))
                    tiles.push([tx, ty, level, this.get_tile_meter_bounds(tx, ty, level)]);
            }
        }
        this.sort_tiles_from_center(tiles, [txmin, tymin, txmax, tymax]);
        return tiles;
    };
    MercatorTileSource.prototype.quadkey_to_tile_xyz = function (quadKey) {
        /**
         * Computes tile x, y and z values based on quadKey.
         */
        var tileX = 0;
        var tileY = 0;
        var tileZ = quadKey.length;
        for (var i = tileZ; i > 0; i--) {
            var value = quadKey.charAt(tileZ - i);
            var mask = 1 << (i - 1);
            switch (value) {
                case '0':
                    continue;
                case '1':
                    tileX |= mask;
                    break;
                case '2':
                    tileY |= mask;
                    break;
                case '3':
                    tileX |= mask;
                    tileY |= mask;
                    break;
                default:
                    throw new TypeError("Invalid Quadkey: " + quadKey);
            }
        }
        return [tileX, tileY, tileZ];
    };
    MercatorTileSource.prototype.tile_xyz_to_quadkey = function (x, y, z) {
        /*
         * Computes quadkey value based on tile x, y and z values.
         */
        var quadkey = "";
        for (var i = z; i > 0; i--) {
            var mask = 1 << (i - 1);
            var digit = 0;
            if ((x & mask) !== 0) {
                digit += 1;
            }
            if ((y & mask) !== 0) {
                digit += 2;
            }
            quadkey += digit.toString();
        }
        return quadkey;
    };
    MercatorTileSource.prototype.children_by_tile_xyz = function (x, y, z) {
        var quadkey = this.tile_xyz_to_quadkey(x, y, z);
        var child_tile_xyz = [];
        for (var i = 0; i <= 3; i++) {
            var _a = this.quadkey_to_tile_xyz(quadkey + i.toString()), x_1 = _a[0], y_1 = _a[1], z_1 = _a[2];
            var b = this.get_tile_meter_bounds(x_1, y_1, z_1);
            child_tile_xyz.push([x_1, y_1, z_1, b]);
        }
        return child_tile_xyz;
    };
    MercatorTileSource.prototype.get_closest_parent_by_tile_xyz = function (x, y, z) {
        var _a, _b, _c;
        var world_x = this.calculate_world_x_by_tile_xyz(x, y, z);
        _a = this.normalize_xyz(x, y, z), x = _a[0], y = _a[1], z = _a[2];
        var quadkey = this.tile_xyz_to_quadkey(x, y, z);
        while (quadkey.length > 0) {
            quadkey = quadkey.substring(0, quadkey.length - 1);
            _b = this.quadkey_to_tile_xyz(quadkey), x = _b[0], y = _b[1], z = _b[2];
            _c = this.denormalize_xyz(x, y, z, world_x), x = _c[0], y = _c[1], z = _c[2];
            if (this.tile_xyz_to_key(x, y, z) in this.tiles)
                return [x, y, z];
        }
        return [0, 0, 0];
    };
    MercatorTileSource.prototype.normalize_xyz = function (x, y, z) {
        if (this.wrap_around) {
            var tile_count = Math.pow(2, z);
            return [((x % tile_count) + tile_count) % tile_count, y, z];
        }
        else {
            return [x, y, z];
        }
    };
    MercatorTileSource.prototype.denormalize_xyz = function (x, y, z, world_x) {
        return [x + (world_x * Math.pow(2, z)), y, z];
    };
    MercatorTileSource.prototype.denormalize_meters = function (meters_x, meters_y, _level, world_x) {
        return [meters_x + (world_x * 2 * Math.PI * 6378137), meters_y];
    };
    MercatorTileSource.prototype.calculate_world_x_by_tile_xyz = function (x, _y, z) {
        return Math.floor(x / Math.pow(2, z));
    };
    return MercatorTileSource;
}(tile_source_1.TileSource));
exports.MercatorTileSource = MercatorTileSource;
MercatorTileSource.initClass();
