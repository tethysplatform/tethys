"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var mercator_tile_source_1 = require("./mercator_tile_source");
var WMTSTileSource = /** @class */ (function (_super) {
    tslib_1.__extends(WMTSTileSource, _super);
    function WMTSTileSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    WMTSTileSource.initClass = function () {
        this.prototype.type = 'WMTSTileSource';
    };
    WMTSTileSource.prototype.get_image_url = function (x, y, z) {
        var image_url = this.string_lookup_replace(this.url, this.extra_url_vars);
        var _a = this.tms_to_wmts(x, y, z), wx = _a[0], wy = _a[1], wz = _a[2];
        return image_url.replace("{X}", wx.toString())
            .replace('{Y}', wy.toString())
            .replace("{Z}", wz.toString());
    };
    return WMTSTileSource;
}(mercator_tile_source_1.MercatorTileSource));
exports.WMTSTileSource = WMTSTileSource;
WMTSTileSource.initClass();
