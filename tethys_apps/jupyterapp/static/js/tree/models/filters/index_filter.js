"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var filter_1 = require("./filter");
var p = require("core/properties");
var logging_1 = require("core/logging");
var types_1 = require("core/util/types");
var array_1 = require("core/util/array");
var IndexFilter = /** @class */ (function (_super) {
    tslib_1.__extends(IndexFilter, _super);
    function IndexFilter(attrs) {
        return _super.call(this, attrs) || this;
    }
    IndexFilter.initClass = function () {
        this.prototype.type = 'IndexFilter';
        this.define({
            indices: [p.Array, null],
        });
    };
    IndexFilter.prototype.compute_indices = function (_source) {
        if (this.indices != null && this.indices.length >= 0) {
            if (array_1.all(this.indices, types_1.isInteger))
                return this.indices;
            else {
                logging_1.logger.warn("IndexFilter " + this.id + ": indices should be array of integers, defaulting to no filtering");
                return null;
            }
        }
        else {
            logging_1.logger.warn("IndexFilter " + this.id + ": indices was not set, defaulting to no filtering");
            return null;
        }
    };
    return IndexFilter;
}(filter_1.Filter));
exports.IndexFilter = IndexFilter;
IndexFilter.initClass();
