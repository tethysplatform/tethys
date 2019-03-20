"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var filter_1 = require("./filter");
var p = require("core/properties");
var logging_1 = require("core/logging");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var BooleanFilter = /** @class */ (function (_super) {
    tslib_1.__extends(BooleanFilter, _super);
    function BooleanFilter(attrs) {
        return _super.call(this, attrs) || this;
    }
    BooleanFilter.initClass = function () {
        this.prototype.type = 'BooleanFilter';
        this.define({
            booleans: [p.Array, null],
        });
    };
    BooleanFilter.prototype.compute_indices = function (source) {
        var booleans = this.booleans;
        if (booleans != null && booleans.length > 0) {
            if (array_1.all(booleans, types_1.isBoolean)) {
                if (booleans.length !== source.get_length()) {
                    logging_1.logger.warn("BooleanFilter " + this.id + ": length of booleans doesn't match data source");
                }
                return array_1.range(0, booleans.length).filter(function (i) { return booleans[i] === true; });
            }
            else {
                logging_1.logger.warn("BooleanFilter " + this.id + ": booleans should be array of booleans, defaulting to no filtering");
                return null;
            }
        }
        else {
            if (booleans != null && booleans.length == 0)
                logging_1.logger.warn("BooleanFilter " + this.id + ": booleans is empty, defaulting to no filtering");
            else
                logging_1.logger.warn("BooleanFilter " + this.id + ": booleans was not set, defaulting to no filtering");
            return null;
        }
    };
    return BooleanFilter;
}(filter_1.Filter));
exports.BooleanFilter = BooleanFilter;
BooleanFilter.initClass();
