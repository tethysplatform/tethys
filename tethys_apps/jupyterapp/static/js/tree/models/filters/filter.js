"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var p = require("core/properties");
var types_1 = require("core/util/types");
var array_1 = require("core/util/array");
var logging_1 = require("core/logging");
var Filter = /** @class */ (function (_super) {
    tslib_1.__extends(Filter, _super);
    function Filter(attrs) {
        return _super.call(this, attrs) || this;
    }
    Filter.initClass = function () {
        this.prototype.type = 'Filter';
        this.define({
            filter: [p.Array, null],
        });
    };
    Filter.prototype.compute_indices = function (_source) {
        var filter = this.filter;
        if (filter != null && filter.length >= 0) {
            if (types_1.isArrayOf(filter, types_1.isBoolean)) {
                return array_1.range(0, filter.length).filter(function (i) { return filter[i] === true; });
            }
            if (types_1.isArrayOf(filter, types_1.isInteger)) {
                return filter;
            }
            logging_1.logger.warn("Filter " + this.id + ": filter should either be array of only booleans or only integers, defaulting to no filtering");
            return null;
        }
        else {
            logging_1.logger.warn("Filter " + this.id + ": filter was not set to be an array, defaulting to no filtering");
            return null;
        }
    };
    return Filter;
}(model_1.Model));
exports.Filter = Filter;
Filter.initClass();
