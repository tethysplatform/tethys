"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_view_1 = require("core/dom_view");
var visuals = require("core/visuals");
var p = require("core/properties");
var model_1 = require("../../model");
// This shouldn't be a DOMView, but annotations create a mess.
var RendererView = /** @class */ (function (_super) {
    tslib_1.__extends(RendererView, _super);
    function RendererView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RendererView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.plot_view = options.plot_view;
        this.visuals = new visuals.Visuals(this.model);
        this._has_finished = true; // XXX: should be in render() but subclasses don't respect super()
    };
    Object.defineProperty(RendererView.prototype, "plot_model", {
        get: function () {
            return this.plot_view.model;
        },
        enumerable: true,
        configurable: true
    });
    RendererView.prototype.request_render = function () {
        this.plot_view.request_render();
    };
    RendererView.prototype.map_to_screen = function (x, y) {
        return this.plot_view.map_to_screen(x, y, this.model.x_range_name, this.model.y_range_name);
    };
    Object.defineProperty(RendererView.prototype, "needs_clip", {
        get: function () {
            return false;
        },
        enumerable: true,
        configurable: true
    });
    return RendererView;
}(dom_view_1.DOMView));
exports.RendererView = RendererView;
var Renderer = /** @class */ (function (_super) {
    tslib_1.__extends(Renderer, _super);
    function Renderer(attrs) {
        return _super.call(this, attrs) || this;
    }
    Renderer.initClass = function () {
        this.prototype.type = "Renderer";
        this.define({
            level: [p.RenderLevel],
            visible: [p.Bool, true],
        });
    };
    return Renderer;
}(model_1.Model));
exports.Renderer = Renderer;
Renderer.initClass();
