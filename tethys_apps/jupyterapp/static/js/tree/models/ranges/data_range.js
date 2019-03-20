"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var range_1 = require("./range");
var p = require("core/properties");
var DataRange = /** @class */ (function (_super) {
    tslib_1.__extends(DataRange, _super);
    function DataRange(attrs) {
        return _super.call(this, attrs) || this;
    }
    DataRange.initClass = function () {
        this.prototype.type = "DataRange";
        this.define({
            names: [p.Array, []],
            renderers: [p.Array, []],
        });
    };
    return DataRange;
}(range_1.Range));
exports.DataRange = DataRange;
DataRange.initClass();
