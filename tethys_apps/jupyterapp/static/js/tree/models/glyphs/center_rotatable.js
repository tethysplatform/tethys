"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var p = require("core/properties");
var CenterRotatableView = /** @class */ (function (_super) {
    tslib_1.__extends(CenterRotatableView, _super);
    function CenterRotatableView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return CenterRotatableView;
}(xy_glyph_1.XYGlyphView));
exports.CenterRotatableView = CenterRotatableView;
var CenterRotatable = /** @class */ (function (_super) {
    tslib_1.__extends(CenterRotatable, _super);
    function CenterRotatable(attrs) {
        return _super.call(this, attrs) || this;
    }
    CenterRotatable.initClass = function () {
        this.prototype.type = 'CenterRotatable';
        this.mixins(['line', 'fill']);
        this.define({
            angle: [p.AngleSpec, 0],
            width: [p.DistanceSpec],
            height: [p.DistanceSpec],
        });
    };
    return CenterRotatable;
}(xy_glyph_1.XYGlyph));
exports.CenterRotatable = CenterRotatable;
CenterRotatable.initClass();
