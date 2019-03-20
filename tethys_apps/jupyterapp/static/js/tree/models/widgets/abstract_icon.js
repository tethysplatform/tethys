"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var widget_1 = require("./widget");
var AbstractIconView = /** @class */ (function (_super) {
    tslib_1.__extends(AbstractIconView, _super);
    function AbstractIconView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return AbstractIconView;
}(widget_1.WidgetView));
exports.AbstractIconView = AbstractIconView;
var AbstractIcon = /** @class */ (function (_super) {
    tslib_1.__extends(AbstractIcon, _super);
    function AbstractIcon(attrs) {
        return _super.call(this, attrs) || this;
    }
    AbstractIcon.initClass = function () {
        this.prototype.type = "AbstractIcon";
    };
    return AbstractIcon;
}(widget_1.Widget));
exports.AbstractIcon = AbstractIcon;
AbstractIcon.initClass();
