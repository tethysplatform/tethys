"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var basic_tick_formatter_1 = require("./basic_tick_formatter");
var p = require("core/properties");
var projections_1 = require("core/util/projections");
var MercatorTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(MercatorTickFormatter, _super);
    function MercatorTickFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    MercatorTickFormatter.initClass = function () {
        this.prototype.type = 'MercatorTickFormatter';
        this.define({
            dimension: [p.LatLon],
        });
    };
    MercatorTickFormatter.prototype.doFormat = function (ticks, axis) {
        if (this.dimension == null)
            throw new Error("MercatorTickFormatter.dimension not configured");
        if (ticks.length == 0)
            return [];
        var n = ticks.length;
        var proj_ticks = new Array(n);
        if (this.dimension == "lon") {
            for (var i = 0; i < n; i++) {
                var lon = projections_1.wgs84_mercator.inverse([ticks[i], axis.loc])[0];
                proj_ticks[i] = lon;
            }
        }
        else {
            for (var i = 0; i < n; i++) {
                var _a = projections_1.wgs84_mercator.inverse([axis.loc, ticks[i]]), lat = _a[1];
                proj_ticks[i] = lat;
            }
        }
        return _super.prototype.doFormat.call(this, proj_ticks, axis);
    };
    return MercatorTickFormatter;
}(basic_tick_formatter_1.BasicTickFormatter));
exports.MercatorTickFormatter = MercatorTickFormatter;
MercatorTickFormatter.initClass();
