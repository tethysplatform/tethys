"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var ellipse_oval_1 = require("./ellipse_oval");
var OvalView = /** @class */ (function (_super) {
    tslib_1.__extends(OvalView, _super);
    function OvalView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    OvalView.prototype._map_data = function () {
        var sw;
        var n = this._x.length;
        this.sw = new Float64Array(n);
        if (this.model.properties.width.units == "data")
            sw = this.sdist(this.renderer.xscale, this._x, this._width, 'center');
        else
            sw = this._width;
        // oval drawn from bezier curves = ellipse with width reduced by 3/4
        for (var i = 0; i < n; i++)
            this.sw[i] = sw[i] * 0.75;
        if (this.model.properties.height.units == "data")
            this.sh = this.sdist(this.renderer.yscale, this._y, this._height, 'center');
        else
            this.sh = this._height;
    };
    return OvalView;
}(ellipse_oval_1.EllipseOvalView));
exports.OvalView = OvalView;
var Oval = /** @class */ (function (_super) {
    tslib_1.__extends(Oval, _super);
    function Oval(attrs) {
        return _super.call(this, attrs) || this;
    }
    Oval.initClass = function () {
        this.prototype.type = 'Oval';
        this.prototype.default_view = OvalView;
    };
    return Oval;
}(ellipse_oval_1.EllipseOval));
exports.Oval = Oval;
Oval.initClass();
