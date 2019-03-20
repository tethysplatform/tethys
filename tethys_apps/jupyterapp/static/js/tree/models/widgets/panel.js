"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var widget_1 = require("./widget");
var p = require("core/properties");
var dom_1 = require("core/dom");
var PanelView = /** @class */ (function (_super) {
    tslib_1.__extends(PanelView, _super);
    function PanelView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PanelView.prototype.render = function () {
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
    };
    return PanelView;
}(widget_1.WidgetView));
exports.PanelView = PanelView;
var Panel = /** @class */ (function (_super) {
    tslib_1.__extends(Panel, _super);
    function Panel(attrs) {
        return _super.call(this, attrs) || this;
    }
    Panel.initClass = function () {
        this.prototype.type = "Panel";
        this.prototype.default_view = PanelView;
        this.define({
            title: [p.String, ""],
            child: [p.Instance],
            closable: [p.Bool, false],
        });
    };
    return Panel;
}(widget_1.Widget));
exports.Panel = Panel;
Panel.initClass();
