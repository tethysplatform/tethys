"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var filter_1 = require("./filter");
var p = require("core/properties");
var logging_1 = require("core/logging");
var array_1 = require("core/util/array");
var GroupFilter = /** @class */ (function (_super) {
    tslib_1.__extends(GroupFilter, _super);
    function GroupFilter(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.indices = null;
        return _this;
    }
    GroupFilter.initClass = function () {
        this.prototype.type = 'GroupFilter';
        this.define({
            column_name: [p.String],
            group: [p.String],
        });
    };
    GroupFilter.prototype.compute_indices = function (source) {
        var _this = this;
        var column = source.get_column(this.column_name);
        if (column == null) {
            logging_1.logger.warn("group filter: groupby column not found in data source");
            return null;
        }
        else {
            this.indices = array_1.range(0, source.get_length() || 0).filter(function (i) { return column[i] === _this.group; });
            if (this.indices.length === 0) {
                logging_1.logger.warn("group filter: group '" + this.group + "' did not match any values in column '" + this.column_name + "'");
            }
            return this.indices;
        }
    };
    return GroupFilter;
}(filter_1.Filter));
exports.GroupFilter = GroupFilter;
GroupFilter.initClass();
