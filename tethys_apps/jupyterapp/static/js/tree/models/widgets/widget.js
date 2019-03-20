"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var layout_dom_1 = require("../layouts/layout_dom");
var WidgetView = /** @class */ (function (_super) {
    tslib_1.__extends(WidgetView, _super);
    function WidgetView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    WidgetView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-widget");
    };
    WidgetView.prototype.render = function () {
        this._render_classes(); // XXX: because no super()
        // LayoutDOMView sets up lots of helpful things, but
        // it's render method is not suitable for widgets - who
        // should provide their own.
        if (this.model.height != null)
            this.el.style.height = this.model.height + "px";
        if (this.model.width != null)
            this.el.style.width = this.model.width + "px";
    };
    WidgetView.prototype.get_width = function () {
        throw new Error("unused");
    };
    WidgetView.prototype.get_height = function () {
        throw new Error("unused");
    };
    return WidgetView;
}(layout_dom_1.LayoutDOMView));
exports.WidgetView = WidgetView;
var Widget = /** @class */ (function (_super) {
    tslib_1.__extends(Widget, _super);
    function Widget(attrs) {
        return _super.call(this, attrs) || this;
    }
    Widget.initClass = function () {
        this.prototype.type = "Widget";
    };
    return Widget;
}(layout_dom_1.LayoutDOM));
exports.Widget = Widget;
Widget.initClass();
