"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var axis_1 = require("./axis");
var linear_axis_1 = require("./linear_axis");
var mercator_tick_formatter_1 = require("../formatters/mercator_tick_formatter");
var mercator_ticker_1 = require("../tickers/mercator_ticker");
var MercatorAxisView = /** @class */ (function (_super) {
    tslib_1.__extends(MercatorAxisView, _super);
    function MercatorAxisView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return MercatorAxisView;
}(axis_1.AxisView));
exports.MercatorAxisView = MercatorAxisView;
var MercatorAxis = /** @class */ (function (_super) {
    tslib_1.__extends(MercatorAxis, _super);
    function MercatorAxis(attrs) {
        return _super.call(this, attrs) || this;
    }
    MercatorAxis.initClass = function () {
        this.prototype.type = "MercatorAxis";
        this.prototype.default_view = MercatorAxisView;
        this.override({
            ticker: function () { return new mercator_ticker_1.MercatorTicker({ dimension: "lat" }); },
            formatter: function () { return new mercator_tick_formatter_1.MercatorTickFormatter({ dimension: "lat" }); },
        });
    };
    return MercatorAxis;
}(linear_axis_1.LinearAxis));
exports.MercatorAxis = MercatorAxis;
MercatorAxis.initClass();
