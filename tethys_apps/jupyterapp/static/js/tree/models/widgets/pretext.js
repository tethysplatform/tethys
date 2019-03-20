"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var markup_1 = require("./markup");
var dom_1 = require("core/dom");
var PreTextView = /** @class */ (function (_super) {
    tslib_1.__extends(PreTextView, _super);
    function PreTextView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PreTextView.prototype.render = function () {
        _super.prototype.render.call(this);
        var content = dom_1.pre({ style: { overflow: "auto" } }, this.model.text);
        this.markupEl.appendChild(content);
    };
    return PreTextView;
}(markup_1.MarkupView));
exports.PreTextView = PreTextView;
var PreText = /** @class */ (function (_super) {
    tslib_1.__extends(PreText, _super);
    function PreText(attrs) {
        return _super.call(this, attrs) || this;
    }
    PreText.initClass = function () {
        this.prototype.type = "PreText";
        this.prototype.default_view = PreTextView;
    };
    return PreText;
}(markup_1.Markup));
exports.PreText = PreText;
PreText.initClass();
