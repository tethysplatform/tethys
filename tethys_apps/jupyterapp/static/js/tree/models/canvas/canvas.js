"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var layout_canvas_1 = require("core/layout/layout_canvas");
var dom_view_1 = require("core/dom_view");
var solver_1 = require("core/layout/solver");
var logging_1 = require("core/logging");
var p = require("core/properties");
var dom_1 = require("core/dom");
var canvas_1 = require("core/util/canvas");
// fixes up a problem with some versions of IE11
// ref: http://stackoverflow.com/questions/22062313/imagedata-set-in-internetexplorer
if (window.CanvasPixelArray != null) {
    window.CanvasPixelArray.prototype.set = function (arr) {
        for (var i = 0; i < this.length; i++) {
            this[i] = arr[i];
        }
    };
}
var CanvasView = /** @class */ (function (_super) {
    tslib_1.__extends(CanvasView, _super);
    function CanvasView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(CanvasView.prototype, "ctx", {
        get: function () {
            return this._ctx;
        },
        enumerable: true,
        configurable: true
    });
    CanvasView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.map_el = this.model.map ? this.el.appendChild(dom_1.div({ class: "bk-canvas-map" })) : null;
        switch (this.model.output_backend) {
            case "canvas":
            case "webgl": {
                this.canvas_el = this.el.appendChild(dom_1.canvas({ class: "bk-canvas" }));
                var ctx = this.canvas_el.getContext('2d');
                if (ctx == null)
                    throw new Error("unable to obtain 2D rendering context");
                this._ctx = ctx;
                break;
            }
            case "svg": {
                var ctx = new canvas_1.SVGRenderingContext2D();
                this._ctx = ctx;
                this.canvas_el = this.el.appendChild(ctx.getSvg());
                break;
            }
        }
        this.overlays_el = this.el.appendChild(dom_1.div({ class: "bk-canvas-overlays" }));
        this.events_el = this.el.appendChild(dom_1.div({ class: "bk-canvas-events" }));
        canvas_1.fixup_ctx(this._ctx);
        logging_1.logger.debug("CanvasView initialized");
    };
    CanvasView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-canvas-wrapper");
    };
    CanvasView.prototype.get_canvas_element = function () {
        return this.canvas_el;
    };
    CanvasView.prototype.prepare_canvas = function () {
        // Ensure canvas has the correct size, taking HIDPI into account
        var width = this.model._width.value;
        var height = this.model._height.value;
        this.el.style.width = width + "px";
        this.el.style.height = height + "px";
        var pixel_ratio = canvas_1.get_scale_ratio(this.ctx, this.model.use_hidpi, this.model.output_backend);
        this.model.pixel_ratio = pixel_ratio;
        this.canvas_el.style.width = width + "px";
        this.canvas_el.style.height = height + "px";
        // XXX: io.export and canvas2svg don't like this
        // this.canvas_el.width = width*pixel_ratio
        // this.canvas_el.height = height*pixel_ratio
        this.canvas_el.setAttribute("width", "" + width * pixel_ratio);
        this.canvas_el.setAttribute("height", "" + height * pixel_ratio);
        logging_1.logger.debug("Rendering CanvasView with width: " + width + ", height: " + height + ", pixel ratio: " + pixel_ratio);
    };
    CanvasView.prototype.set_dims = function (_a) {
        var width = _a[0], height = _a[1];
        // XXX: for whatever reason we need to protect against those nonsense values,
        //      that appear in the middle of updating layout. Otherwise we would get
        //      all possible errors from the layout solver.
        if (width <= 0 || height <= 0)
            return;
        if (width != this.model._width.value) {
            if (this._width_constraint != null && this.solver.has_constraint(this._width_constraint))
                this.solver.remove_constraint(this._width_constraint);
            this._width_constraint = solver_1.EQ(this.model._width, -width);
            this.solver.add_constraint(this._width_constraint);
        }
        if (height != this.model._height.value) {
            if (this._height_constraint != null && this.solver.has_constraint(this._height_constraint))
                this.solver.remove_constraint(this._height_constraint);
            this._height_constraint = solver_1.EQ(this.model._height, -height);
            this.solver.add_constraint(this._height_constraint);
        }
        this.solver.update_variables();
    };
    return CanvasView;
}(dom_view_1.DOMView));
exports.CanvasView = CanvasView;
var Canvas = /** @class */ (function (_super) {
    tslib_1.__extends(Canvas, _super);
    function Canvas(attrs) {
        return _super.call(this, attrs) || this;
    }
    Canvas.initClass = function () {
        this.prototype.type = "Canvas";
        this.prototype.default_view = CanvasView;
        this.internal({
            map: [p.Boolean, false],
            use_hidpi: [p.Boolean, true],
            pixel_ratio: [p.Number, 1],
            output_backend: [p.OutputBackend, "canvas"],
        });
    };
    Object.defineProperty(Canvas.prototype, "panel", {
        get: function () {
            return this;
        },
        enumerable: true,
        configurable: true
    });
    return Canvas;
}(layout_canvas_1.LayoutCanvas));
exports.Canvas = Canvas;
Canvas.initClass();
