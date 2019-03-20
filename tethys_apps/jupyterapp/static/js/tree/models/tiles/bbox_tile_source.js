"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var mercator_tile_source_1 = require("./mercator_tile_source");
var p = require("core/properties");
var BBoxTileSource = /** @class */ (function (_super) {
    tslib_1.__extends(BBoxTileSource, _super);
    function BBoxTileSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    BBoxTileSource.initClass = function () {
        this.prototype.type = 'BBoxTileSource';
        this.define({
            use_latlon: [p.Bool, false],
        });
    };
    BBoxTileSource.prototype.get_image_url = function (x, y, z) {
        var _a, _b;
        var image_url = this.string_lookup_replace(this.url, this.extra_url_vars);
        var xmax, xmin, ymax, ymin;
        if (this.use_latlon)
            _a = this.get_tile_geographic_bounds(x, y, z), xmin = _a[0], ymin = _a[1], xmax = _a[2], ymax = _a[3];
        else
            _b = this.get_tile_meter_bounds(x, y, z), xmin = _b[0], ymin = _b[1], xmax = _b[2], ymax = _b[3];
        return image_url.replace("{XMIN}", xmin.toString())
            .replace("{YMIN}", ymin.toString())
            .replace("{XMAX}", xmax.toString())
            .replace("{YMAX}", ymax.toString());
    };
    return BBoxTileSource;
}(mercator_tile_source_1.MercatorTileSource));
exports.BBoxTileSource = BBoxTileSource;
BBoxTileSource.initClass();
