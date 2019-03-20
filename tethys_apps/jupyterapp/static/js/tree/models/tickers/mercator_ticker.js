"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var basic_ticker_1 = require("./basic_ticker");
var p = require("core/properties");
var projections_1 = require("core/util/projections");
var MercatorTicker = /** @class */ (function (_super) {
    tslib_1.__extends(MercatorTicker, _super);
    function MercatorTicker(attrs) {
        return _super.call(this, attrs) || this;
    }
    MercatorTicker.initClass = function () {
        this.prototype.type = "MercatorTicker";
        this.define({
            dimension: [p.LatLon],
        });
    };
    MercatorTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, cross_loc, desired_n_ticks) {
        var _a, _b, _c, _d, _e;
        if (this.dimension == null) {
            throw new Error("MercatorTicker.dimension not configured");
        }
        _a = projections_1.clip_mercator(data_low, data_high, this.dimension), data_low = _a[0], data_high = _a[1];
        var proj_low, proj_high, proj_cross_loc;
        if (this.dimension === "lon") {
            _b = projections_1.wgs84_mercator.inverse([data_low, cross_loc]), proj_low = _b[0], proj_cross_loc = _b[1];
            _c = projections_1.wgs84_mercator.inverse([data_high, cross_loc]), proj_high = _c[0], proj_cross_loc = _c[1];
        }
        else {
            _d = projections_1.wgs84_mercator.inverse([cross_loc, data_low]), proj_cross_loc = _d[0], proj_low = _d[1];
            _e = projections_1.wgs84_mercator.inverse([cross_loc, data_high]), proj_cross_loc = _e[0], proj_high = _e[1];
        }
        var proj_ticks = _super.prototype.get_ticks_no_defaults.call(this, proj_low, proj_high, cross_loc, desired_n_ticks);
        var major = [];
        var minor = [];
        if (this.dimension === "lon") {
            for (var _i = 0, _f = proj_ticks.major; _i < _f.length; _i++) {
                var tick = _f[_i];
                if (projections_1.in_bounds(tick, 'lon')) {
                    var lon = projections_1.wgs84_mercator.forward([tick, proj_cross_loc])[0];
                    major.push(lon);
                }
            }
            for (var _g = 0, _h = proj_ticks.minor; _g < _h.length; _g++) {
                var tick = _h[_g];
                if (projections_1.in_bounds(tick, 'lon')) {
                    var lon = projections_1.wgs84_mercator.forward([tick, proj_cross_loc])[0];
                    minor.push(lon);
                }
            }
        }
        else {
            for (var _j = 0, _k = proj_ticks.major; _j < _k.length; _j++) {
                var tick = _k[_j];
                if (projections_1.in_bounds(tick, 'lat')) {
                    var _l = projections_1.wgs84_mercator.forward([proj_cross_loc, tick]), lat = _l[1];
                    major.push(lat);
                }
            }
            for (var _m = 0, _o = proj_ticks.minor; _m < _o.length; _m++) {
                var tick = _o[_m];
                if (projections_1.in_bounds(tick, 'lat')) {
                    var _p = projections_1.wgs84_mercator.forward([proj_cross_loc, tick]), lat = _p[1];
                    minor.push(lat);
                }
            }
        }
        return {
            major: major,
            minor: minor,
        };
    };
    return MercatorTicker;
}(basic_ticker_1.BasicTicker));
exports.MercatorTicker = MercatorTicker;
MercatorTicker.initClass();
