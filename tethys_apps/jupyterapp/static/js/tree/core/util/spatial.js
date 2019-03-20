"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var FlatBush = require("flatbush");
var bbox_1 = require("./bbox");
var SpatialIndex = /** @class */ (function () {
    function SpatialIndex(points) {
        this.points = points;
        this.index = null;
        if (points.length > 0) {
            this.index = new FlatBush(points.length);
            for (var _i = 0, points_1 = points; _i < points_1.length; _i++) {
                var p = points_1[_i];
                var minX = p.minX, minY = p.minY, maxX = p.maxX, maxY = p.maxY;
                this.index.add(minX, minY, maxX, maxY);
            }
            this.index.finish();
        }
    }
    Object.defineProperty(SpatialIndex.prototype, "bbox", {
        get: function () {
            if (this.index == null)
                return bbox_1.empty();
            else {
                var _a = this.index, minX = _a.minX, minY = _a.minY, maxX = _a.maxX, maxY = _a.maxY;
                return { minX: minX, minY: minY, maxX: maxX, maxY: maxY };
            }
        },
        enumerable: true,
        configurable: true
    });
    SpatialIndex.prototype.search = function (rect) {
        var _this = this;
        if (this.index == null)
            return [];
        else {
            var minX = rect.minX, minY = rect.minY, maxX = rect.maxX, maxY = rect.maxY;
            var indices = this.index.search(minX, minY, maxX, maxY);
            return indices.map(function (j) { return _this.points[j]; });
        }
    };
    SpatialIndex.prototype.indices = function (rect) {
        return this.search(rect).map(function (_a) {
            var i = _a.i;
            return i;
        });
    };
    return SpatialIndex;
}());
exports.SpatialIndex = SpatialIndex;
