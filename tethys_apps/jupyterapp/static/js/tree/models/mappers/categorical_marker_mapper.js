"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var categorical_mapper_1 = require("./categorical_mapper");
var mapper_1 = require("./mapper");
var p = require("core/properties");
var CategoricalMarkerMapper = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalMarkerMapper, _super);
    function CategoricalMarkerMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalMarkerMapper.initClass = function () {
        this.prototype.type = "CategoricalMarkerMapper";
        this.define({
            factors: [p.Array],
            markers: [p.Array],
            start: [p.Number, 0],
            end: [p.Number],
            default_value: [p.String, "circle"],
        });
    };
    CategoricalMarkerMapper.prototype.v_compute = function (xs) {
        var values = new Array(xs.length);
        categorical_mapper_1.cat_v_compute(xs, this.factors, this.markers, values, this.start, this.end, this.default_value);
        return values;
    };
    return CategoricalMarkerMapper;
}(mapper_1.Mapper));
exports.CategoricalMarkerMapper = CategoricalMarkerMapper;
CategoricalMarkerMapper.initClass();
