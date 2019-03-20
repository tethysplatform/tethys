"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var renderer_1 = require("./renderer");
var p = require("core/properties");
var GuideRendererView = /** @class */ (function (_super) {
    tslib_1.__extends(GuideRendererView, _super);
    function GuideRendererView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return GuideRendererView;
}(renderer_1.RendererView));
exports.GuideRendererView = GuideRendererView;
var GuideRenderer = /** @class */ (function (_super) {
    tslib_1.__extends(GuideRenderer, _super);
    function GuideRenderer(attrs) {
        return _super.call(this, attrs) || this;
    }
    GuideRenderer.initClass = function () {
        this.prototype.type = "GuideRenderer";
        this.define({
            plot: [p.Instance],
        });
        this.override({
            level: "overlay",
        });
    };
    return GuideRenderer;
}(renderer_1.Renderer));
exports.GuideRenderer = GuideRenderer;
GuideRenderer.initClass();
