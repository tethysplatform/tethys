"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var dom_1 = require("core/dom");
var widget_1 = require("./widget");
var MarkupView = /** @class */ (function (_super) {
    tslib_1.__extends(MarkupView, _super);
    function MarkupView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MarkupView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    MarkupView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    MarkupView.prototype.render = function () {
        _super.prototype.render.call(this);
        dom_1.empty(this.el);
        var style = tslib_1.__assign({ width: this.model.width + "px", height: this.model.height + "px" }, this.model.style);
        this.markupEl = dom_1.div({ style: style });
        this.el.appendChild(this.markupEl);
    };
    return MarkupView;
}(widget_1.WidgetView));
exports.MarkupView = MarkupView;
var Markup = /** @class */ (function (_super) {
    tslib_1.__extends(Markup, _super);
    function Markup(attrs) {
        return _super.call(this, attrs) || this;
    }
    Markup.initClass = function () {
        this.prototype.type = "Markup";
        this.define({
            text: [p.String, ''],
            style: [p.Any, {}],
        });
    };
    return Markup;
}(widget_1.Widget));
exports.Markup = Markup;
Markup.initClass();
