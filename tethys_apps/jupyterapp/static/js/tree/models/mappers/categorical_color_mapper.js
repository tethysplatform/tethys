"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var categorical_mapper_1 = require("./categorical_mapper");
var color_mapper_1 = require("./color_mapper");
var p = require("core/properties");
var CategoricalColorMapper = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalColorMapper, _super);
    function CategoricalColorMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalColorMapper.initClass = function () {
        this.prototype.type = "CategoricalColorMapper";
        this.define({
            factors: [p.Array],
            start: [p.Number, 0],
            end: [p.Number],
        });
    };
    CategoricalColorMapper.prototype._v_compute = function (data, values, palette, _a) {
        var nan_color = _a.nan_color;
        categorical_mapper_1.cat_v_compute(data, this.factors, palette, values, this.start, this.end, nan_color);
    };
    return CategoricalColorMapper;
}(color_mapper_1.ColorMapper));
exports.CategoricalColorMapper = CategoricalColorMapper;
CategoricalColorMapper.initClass();
