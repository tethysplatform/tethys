"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var ellipse_oval_1 = require("./ellipse_oval");
var EllipseView = /** @class */ (function (_super) {
    tslib_1.__extends(EllipseView, _super);
    function EllipseView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return EllipseView;
}(ellipse_oval_1.EllipseOvalView));
exports.EllipseView = EllipseView;
var Ellipse = /** @class */ (function (_super) {
    tslib_1.__extends(Ellipse, _super);
    function Ellipse(attrs) {
        return _super.call(this, attrs) || this;
    }
    Ellipse.initClass = function () {
        this.prototype.type = 'Ellipse';
        this.prototype.default_view = EllipseView;
    };
    return Ellipse;
}(ellipse_oval_1.EllipseOval));
exports.Ellipse = Ellipse;
Ellipse.initClass();
