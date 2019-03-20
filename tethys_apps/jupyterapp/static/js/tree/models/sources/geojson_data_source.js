"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var columnar_data_source_1 = require("./columnar_data_source");
var logging_1 = require("core/logging");
var p = require("core/properties");
var array_1 = require("core/util/array");
var GeoJSONDataSource = /** @class */ (function (_super) {
    tslib_1.__extends(GeoJSONDataSource, _super);
    function GeoJSONDataSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    GeoJSONDataSource.initClass = function () {
        this.prototype.type = 'GeoJSONDataSource';
        this.define({
            geojson: [p.Any],
        });
        this.internal({
            data: [p.Any, {}],
        });
    };
    GeoJSONDataSource.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._update_data();
    };
    GeoJSONDataSource.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.properties.geojson.change, function () { return _this._update_data(); });
    };
    GeoJSONDataSource.prototype._update_data = function () {
        this.data = this.geojson_to_column_data();
    };
    GeoJSONDataSource.prototype._get_new_list_array = function (length) {
        return array_1.range(0, length).map(function (_i) { return []; });
    };
    GeoJSONDataSource.prototype._get_new_nan_array = function (length) {
        return array_1.range(0, length).map(function (_i) { return NaN; });
    };
    GeoJSONDataSource.prototype._add_properties = function (item, data, i, item_count) {
        var properties = item.properties || {};
        for (var property in properties) {
            if (!data.hasOwnProperty(property))
                data[property] = this._get_new_nan_array(item_count);
            data[property][i] = properties[property];
        }
    };
    GeoJSONDataSource.prototype._add_geometry = function (geometry, data, i) {
        function orNaN(v) {
            return v != null ? v : NaN;
        }
        function flatten(acc, item) {
            return acc.concat([[NaN, NaN, NaN]]).concat(item);
        }
        switch (geometry.type) {
            case "Point": {
                var _a = geometry.coordinates, x = _a[0], y = _a[1], z = _a[2];
                data.x[i] = x;
                data.y[i] = y;
                data.z[i] = orNaN(z);
                break;
            }
            case "LineString": {
                var coordinates = geometry.coordinates;
                for (var j = 0; j < coordinates.length; j++) {
                    var _b = coordinates[j], x = _b[0], y = _b[1], z = _b[2];
                    data.xs[i][j] = x;
                    data.ys[i][j] = y;
                    data.zs[i][j] = orNaN(z);
                }
                break;
            }
            case "Polygon": {
                if (geometry.coordinates.length > 1)
                    logging_1.logger.warn('Bokeh does not support Polygons with holes in, only exterior ring used.');
                var exterior_ring = geometry.coordinates[0];
                for (var j = 0; j < exterior_ring.length; j++) {
                    var _c = exterior_ring[j], x = _c[0], y = _c[1], z = _c[2];
                    data.xs[i][j] = x;
                    data.ys[i][j] = y;
                    data.zs[i][j] = orNaN(z);
                }
                break;
            }
            case "MultiPoint": {
                logging_1.logger.warn('MultiPoint not supported in Bokeh');
                break;
            }
            case "MultiLineString": {
                var coordinates = geometry.coordinates.reduce(flatten);
                for (var j = 0; j < coordinates.length; j++) {
                    var _d = coordinates[j], x = _d[0], y = _d[1], z = _d[2];
                    data.xs[i][j] = x;
                    data.ys[i][j] = y;
                    data.zs[i][j] = orNaN(z);
                }
                break;
            }
            case "MultiPolygon": {
                var exterior_rings = [];
                for (var _e = 0, _f = geometry.coordinates; _e < _f.length; _e++) {
                    var polygon = _f[_e];
                    if (polygon.length > 1)
                        logging_1.logger.warn('Bokeh does not support Polygons with holes in, only exterior ring used.');
                    exterior_rings.push(polygon[0]);
                }
                var coordinates = exterior_rings.reduce(flatten);
                for (var j = 0; j < coordinates.length; j++) {
                    var _g = coordinates[j], x = _g[0], y = _g[1], z = _g[2];
                    data.xs[i][j] = x;
                    data.ys[i][j] = y;
                    data.zs[i][j] = orNaN(z);
                }
                break;
            }
            default:
                throw new Error("Invalid GeoJSON geometry type: " + geometry.type);
        }
    };
    GeoJSONDataSource.prototype.geojson_to_column_data = function () {
        var geojson = JSON.parse(this.geojson);
        var items;
        switch (geojson.type) {
            case "GeometryCollection": {
                if (geojson.geometries == null)
                    throw new Error('No geometries found in GeometryCollection');
                if (geojson.geometries.length === 0)
                    throw new Error('geojson.geometries must have one or more items');
                items = geojson.geometries;
                break;
            }
            case "FeatureCollection": {
                if (geojson.features == null)
                    throw new Error('No features found in FeaturesCollection');
                if (geojson.features.length == 0)
                    throw new Error('geojson.features must have one or more items');
                items = geojson.features;
                break;
            }
            default:
                throw new Error('Bokeh only supports type GeometryCollection and FeatureCollection at top level');
        }
        var item_count = 0;
        for (var _a = 0, items_1 = items; _a < items_1.length; _a++) {
            var item = items_1[_a];
            var geometry = item.type === 'Feature' ? item.geometry : item;
            if (geometry.type == 'GeometryCollection')
                item_count += geometry.geometries.length;
            else
                item_count += 1;
        }
        var data = {
            x: this._get_new_nan_array(item_count),
            y: this._get_new_nan_array(item_count),
            z: this._get_new_nan_array(item_count),
            xs: this._get_new_list_array(item_count),
            ys: this._get_new_list_array(item_count),
            zs: this._get_new_list_array(item_count),
        };
        var arr_index = 0;
        for (var _b = 0, items_2 = items; _b < items_2.length; _b++) {
            var item = items_2[_b];
            var geometry = item.type == 'Feature' ? item.geometry : item;
            if (geometry.type == "GeometryCollection") {
                for (var _c = 0, _d = geometry.geometries; _c < _d.length; _c++) {
                    var g = _d[_c];
                    this._add_geometry(g, data, arr_index);
                    if (item.type === 'Feature')
                        this._add_properties(item, data, arr_index, item_count);
                    arr_index += 1;
                }
            }
            else {
                this._add_geometry(geometry, data, arr_index);
                if (item.type === 'Feature')
                    this._add_properties(item, data, arr_index, item_count);
                arr_index += 1;
            }
        }
        return data;
    };
    return GeoJSONDataSource;
}(columnar_data_source_1.ColumnarDataSource));
exports.GeoJSONDataSource = GeoJSONDataSource;
GeoJSONDataSource.initClass();
