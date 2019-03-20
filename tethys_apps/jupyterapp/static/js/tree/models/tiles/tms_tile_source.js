"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var mercator_tile_source_1 = require("./mercator_tile_source");
var TMSTileSource = /** @class */ (function (_super) {
    tslib_1.__extends(TMSTileSource, _super);
    function TMSTileSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    TMSTileSource.initClass = function () {
        this.prototype.type = 'TMSTileSource';
    };
    TMSTileSource.prototype.get_image_url = function (x, y, z) {
        var image_url = this.string_lookup_replace(this.url, this.extra_url_vars);
        return image_url.replace("{X}", x.toString())
            .replace('{Y}', y.toString())
            .replace("{Z}", z.toString());
    };
    return TMSTileSource;
}(mercator_tile_source_1.MercatorTileSource));
exports.TMSTileSource = TMSTileSource;
TMSTileSource.initClass();
