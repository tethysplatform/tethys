"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var widget_1 = require("./widget");
var p = require("core/properties");
var InputWidgetView = /** @class */ (function (_super) {
    tslib_1.__extends(InputWidgetView, _super);
    function InputWidgetView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    InputWidgetView.prototype.change_input = function () {
        if (this.model.callback != null)
            this.model.callback.execute(this.model);
    };
    return InputWidgetView;
}(widget_1.WidgetView));
exports.InputWidgetView = InputWidgetView;
var InputWidget = /** @class */ (function (_super) {
    tslib_1.__extends(InputWidget, _super);
    function InputWidget(attrs) {
        return _super.call(this, attrs) || this;
    }
    InputWidget.initClass = function () {
        this.prototype.type = "InputWidget";
        this.prototype.default_view = InputWidgetView;
        this.define({
            title: [p.String, ''],
            callback: [p.Instance],
        });
    };
    return InputWidget;
}(widget_1.Widget));
exports.InputWidget = InputWidget;
InputWidget.initClass();
