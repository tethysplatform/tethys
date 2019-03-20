"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var box_1 = require("./box");
var p = require("core/properties");
var HBarView = /** @class */ (function (_super) {
    tslib_1.__extends(HBarView, _super);
    function HBarView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    HBarView.prototype.scenterx = function (i) {
        return (this.sleft[i] + this.sright[i]) / 2;
    };
    HBarView.prototype.scentery = function (i) {
        return this.sy[i];
    };
    HBarView.prototype._index_data = function () {
        return this._index_box(this._y.length);
    };
    HBarView.prototype._lrtb = function (i) {
        var l = Math.min(this._left[i], this._right[i]);
        var r = Math.max(this._left[i], this._right[i]);
        var t = this._y[i] + 0.5 * this._height[i];
        var b = this._y[i] - 0.5 * this._height[i];
        return [l, r, t, b];
    };
    HBarView.prototype._map_data = function () {
        this.sy = this.renderer.yscale.v_compute(this._y);
        this.sh = this.sdist(this.renderer.yscale, this._y, this._height, "center");
        this.sleft = this.renderer.xscale.v_compute(this._left);
        this.sright = this.renderer.xscale.v_compute(this._right);
        var n = this.sy.length;
        this.stop = new Float64Array(n);
        this.sbottom = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            this.stop[i] = this.sy[i] - this.sh[i] / 2;
            this.sbottom[i] = this.sy[i] + this.sh[i] / 2;
        }
        this._clamp_viewport();
    };
    return HBarView;
}(box_1.BoxView));
exports.HBarView = HBarView;
var HBar = /** @class */ (function (_super) {
    tslib_1.__extends(HBar, _super);
    function HBar(attrs) {
        return _super.call(this, attrs) || this;
    }
    HBar.initClass = function () {
        this.prototype.type = 'HBar';
        this.prototype.default_view = HBarView;
        this.coords([['left', 'y']]);
        this.define({
            height: [p.DistanceSpec],
            right: [p.NumberSpec],
        });
        this.override({ left: 0 });
    };
    return HBar;
}(box_1.Box));
exports.HBar = HBar;
HBar.initClass();
