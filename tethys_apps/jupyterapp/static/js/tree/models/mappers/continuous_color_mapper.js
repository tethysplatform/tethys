"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var color_mapper_1 = require("./color_mapper");
var p = require("core/properties");
var ContinuousColorMapper = /** @class */ (function (_super) {
    tslib_1.__extends(ContinuousColorMapper, _super);
    function ContinuousColorMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    ContinuousColorMapper.initClass = function () {
        this.prototype.type = "ContinuousColorMapper";
        this.define({
            high: [p.Number],
            low: [p.Number],
            high_color: [p.Color],
            low_color: [p.Color],
        });
    };
    ContinuousColorMapper.prototype._colors = function (conv) {
        return tslib_1.__assign({}, _super.prototype._colors.call(this, conv), { low_color: this.low_color != null ? conv(this.low_color) : undefined, high_color: this.high_color != null ? conv(this.high_color) : undefined });
    };
    return ContinuousColorMapper;
}(color_mapper_1.ColorMapper));
exports.ContinuousColorMapper = ContinuousColorMapper;
ContinuousColorMapper.initClass();
