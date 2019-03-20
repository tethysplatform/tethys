"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var mercator_tile_source_1 = require("./mercator_tile_source");
var QUADKEYTileSource = /** @class */ (function (_super) {
    tslib_1.__extends(QUADKEYTileSource, _super);
    function QUADKEYTileSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    QUADKEYTileSource.initClass = function () {
        this.prototype.type = 'QUADKEYTileSource';
    };
    QUADKEYTileSource.prototype.get_image_url = function (x, y, z) {
        var image_url = this.string_lookup_replace(this.url, this.extra_url_vars);
        var _a = this.tms_to_wmts(x, y, z), wx = _a[0], wy = _a[1], wz = _a[2];
        var quadKey = this.tile_xyz_to_quadkey(wx, wy, wz);
        return image_url.replace("{Q}", quadKey);
    };
    return QUADKEYTileSource;
}(mercator_tile_source_1.MercatorTileSource));
exports.QUADKEYTileSource = QUADKEYTileSource;
QUADKEYTileSource.initClass();
