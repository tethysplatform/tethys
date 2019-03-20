"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var markup_1 = require("./markup");
var dom_1 = require("core/dom");
var ParagraphView = /** @class */ (function (_super) {
    tslib_1.__extends(ParagraphView, _super);
    function ParagraphView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ParagraphView.prototype.render = function () {
        _super.prototype.render.call(this);
        // This overrides default user-agent styling and helps layout work
        var content = dom_1.p({ style: { margin: 0 } }, this.model.text);
        this.markupEl.appendChild(content);
    };
    return ParagraphView;
}(markup_1.MarkupView));
exports.ParagraphView = ParagraphView;
var Paragraph = /** @class */ (function (_super) {
    tslib_1.__extends(Paragraph, _super);
    function Paragraph(attrs) {
        return _super.call(this, attrs) || this;
    }
    Paragraph.initClass = function () {
        this.prototype.type = "Paragraph";
        this.prototype.default_view = ParagraphView;
    };
    return Paragraph;
}(markup_1.Markup));
exports.Paragraph = Paragraph;
Paragraph.initClass();
