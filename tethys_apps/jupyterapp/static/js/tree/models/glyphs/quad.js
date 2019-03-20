"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var box_1 = require("./box");
var QuadView = /** @class */ (function (_super) {
    tslib_1.__extends(QuadView, _super);
    function QuadView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    QuadView.prototype.get_anchor_point = function (anchor, i, _spt) {
        var left = Math.min(this.sleft[i], this.sright[i]);
        var right = Math.max(this.sright[i], this.sleft[i]);
        var top = Math.min(this.stop[i], this.sbottom[i]); // screen coordinates !!!
        var bottom = Math.max(this.sbottom[i], this.stop[i]); //
        switch (anchor) {
            case "top_left": return { x: left, y: top };
            case "top_center": return { x: (left + right) / 2, y: top };
            case "top_right": return { x: right, y: top };
            case "center_right": return { x: right, y: (top + bottom) / 2 };
            case "bottom_right": return { x: right, y: bottom };
            case "bottom_center": return { x: (left + right) / 2, y: bottom };
            case "bottom_left": return { x: left, y: bottom };
            case "center_left": return { x: left, y: (top + bottom) / 2 };
            case "center": return { x: (left + right) / 2, y: (top + bottom) / 2 };
            default: return null;
        }
    };
    QuadView.prototype.scenterx = function (i) {
        return (this.sleft[i] + this.sright[i]) / 2;
    };
    QuadView.prototype.scentery = function (i) {
        return (this.stop[i] + this.sbottom[i]) / 2;
    };
    QuadView.prototype._index_data = function () {
        return this._index_box(this._right.length);
    };
    QuadView.prototype._lrtb = function (i) {
        var l = this._left[i];
        var r = this._right[i];
        var t = this._top[i];
        var b = this._bottom[i];
        return [l, r, t, b];
    };
    return QuadView;
}(box_1.BoxView));
exports.QuadView = QuadView;
var Quad = /** @class */ (function (_super) {
    tslib_1.__extends(Quad, _super);
    function Quad(attrs) {
        return _super.call(this, attrs) || this;
    }
    Quad.initClass = function () {
        this.prototype.type = 'Quad';
        this.prototype.default_view = QuadView;
        this.coords([['right', 'bottom'], ['left', 'top']]);
    };
    return Quad;
}(box_1.Box));
exports.Quad = Quad;
Quad.initClass();
