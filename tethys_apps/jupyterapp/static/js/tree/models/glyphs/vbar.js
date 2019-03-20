"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var box_1 = require("./box");
var p = require("core/properties");
var VBarView = /** @class */ (function (_super) {
    tslib_1.__extends(VBarView, _super);
    function VBarView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    VBarView.prototype.scenterx = function (i) {
        return this.sx[i];
    };
    VBarView.prototype.scentery = function (i) {
        return (this.stop[i] + this.sbottom[i]) / 2;
    };
    VBarView.prototype._index_data = function () {
        return this._index_box(this._x.length);
    };
    VBarView.prototype._lrtb = function (i) {
        var l = this._x[i] - (this._width[i] / 2);
        var r = this._x[i] + (this._width[i] / 2);
        var t = Math.max(this._top[i], this._bottom[i]);
        var b = Math.min(this._top[i], this._bottom[i]);
        return [l, r, t, b];
    };
    VBarView.prototype._map_data = function () {
        this.sx = this.renderer.xscale.v_compute(this._x);
        this.sw = this.sdist(this.renderer.xscale, this._x, this._width, "center");
        this.stop = this.renderer.yscale.v_compute(this._top);
        this.sbottom = this.renderer.yscale.v_compute(this._bottom);
        var n = this.sx.length;
        this.sleft = new Float64Array(n);
        this.sright = new Float64Array(n);
        for (var i = 0; i < n; i++) {
            this.sleft[i] = this.sx[i] - this.sw[i] / 2;
            this.sright[i] = this.sx[i] + this.sw[i] / 2;
        }
        this._clamp_viewport();
    };
    return VBarView;
}(box_1.BoxView));
exports.VBarView = VBarView;
var VBar = /** @class */ (function (_super) {
    tslib_1.__extends(VBar, _super);
    function VBar(attrs) {
        return _super.call(this, attrs) || this;
    }
    VBar.initClass = function () {
        this.prototype.type = 'VBar';
        this.prototype.default_view = VBarView;
        this.coords([['x', 'bottom']]);
        this.define({
            width: [p.DistanceSpec],
            top: [p.NumberSpec],
        });
        this.override({
            bottom: 0,
        });
    };
    return VBar;
}(box_1.Box));
exports.VBar = VBar;
VBar.initClass();
