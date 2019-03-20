"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var column_data_source_1 = require("./column_data_source");
var p = require("core/properties");
var RemoteDataSource = /** @class */ (function (_super) {
    tslib_1.__extends(RemoteDataSource, _super);
    function RemoteDataSource(attrs) {
        return _super.call(this, attrs) || this;
    }
    RemoteDataSource.prototype.get_column = function (colname) {
        var column = this.data[colname];
        return column != null ? column : [];
    };
    RemoteDataSource.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.setup();
    };
    RemoteDataSource.initClass = function () {
        this.prototype.type = 'RemoteDataSource';
        this.define({
            data_url: [p.String],
            polling_interval: [p.Number],
        });
    };
    return RemoteDataSource;
}(column_data_source_1.ColumnDataSource));
exports.RemoteDataSource = RemoteDataSource;
RemoteDataSource.initClass();
