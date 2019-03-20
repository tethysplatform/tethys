"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var signaling_1 = require("core/signaling");
var dom_1 = require("core/dom");
var p = require("core/properties");
var bbox_1 = require("core/util/bbox");
exports.EDGE_TOLERANCE = 2.5;
var BoxAnnotationView = /** @class */ (function (_super) {
    tslib_1.__extends(BoxAnnotationView, _super);
    function BoxAnnotationView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    BoxAnnotationView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.plot_view.canvas_overlays.appendChild(this.el);
        this.el.classList.add("bk-shading");
        dom_1.hide(this.el);
    };
    BoxAnnotationView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        // need to respond to either normal BB change events or silent
        // "data only updates" that tools might want to use
        if (this.model.render_mode == 'css') {
            // dispatch CSS update immediately
            this.connect(this.model.change, function () { return _this.render(); });
            this.connect(this.model.data_update, function () { return _this.render(); });
        }
        else {
            this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
            this.connect(this.model.data_update, function () { return _this.plot_view.request_render(); });
        }
    };
    BoxAnnotationView.prototype.render = function () {
        var _this = this;
        if (!this.model.visible && this.model.render_mode == 'css')
            dom_1.hide(this.el);
        if (!this.model.visible)
            return;
        // don't render if *all* position are null
        if (this.model.left == null && this.model.right == null && this.model.top == null && this.model.bottom == null) {
            dom_1.hide(this.el);
            return;
        }
        var frame = this.plot_model.frame;
        var xscale = frame.xscales[this.model.x_range_name];
        var yscale = frame.yscales[this.model.y_range_name];
        var _calc_dim = function (dim, dim_units, scale, view, frame_extrema) {
            var sdim;
            if (dim != null) {
                if (_this.model.screen)
                    sdim = dim;
                else {
                    if (dim_units == 'data')
                        sdim = scale.compute(dim);
                    else
                        sdim = view.compute(dim);
                }
            }
            else
                sdim = frame_extrema;
            return sdim;
        };
        this.sleft = _calc_dim(this.model.left, this.model.left_units, xscale, frame.xview, frame._left.value);
        this.sright = _calc_dim(this.model.right, this.model.right_units, xscale, frame.xview, frame._right.value);
        this.stop = _calc_dim(this.model.top, this.model.top_units, yscale, frame.yview, frame._top.value);
        this.sbottom = _calc_dim(this.model.bottom, this.model.bottom_units, yscale, frame.yview, frame._bottom.value);
        var draw = this.model.render_mode == 'css' ? this._css_box.bind(this) : this._canvas_box.bind(this);
        draw(this.sleft, this.sright, this.sbottom, this.stop);
    };
    BoxAnnotationView.prototype._css_box = function (sleft, sright, sbottom, stop) {
        var line_width = this.model.properties.line_width.value();
        var sw = Math.floor(sright - sleft) - line_width;
        var sh = Math.floor(sbottom - stop) - line_width;
        this.el.style.left = sleft + "px";
        this.el.style.width = sw + "px";
        this.el.style.top = stop + "px";
        this.el.style.height = sh + "px";
        this.el.style.borderWidth = line_width + "px";
        this.el.style.borderColor = this.model.properties.line_color.value();
        this.el.style.backgroundColor = this.model.properties.fill_color.value();
        this.el.style.opacity = this.model.properties.fill_alpha.value();
        // try our best to honor line dashing in some way, if we can
        var ld = this.model.properties.line_dash.value().length < 2 ? "solid" : "dashed";
        this.el.style.borderStyle = ld;
        dom_1.show(this.el);
    };
    BoxAnnotationView.prototype._canvas_box = function (sleft, sright, sbottom, stop) {
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        ctx.beginPath();
        ctx.rect(sleft, stop, sright - sleft, sbottom - stop);
        this.visuals.fill.set_value(ctx);
        ctx.fill();
        this.visuals.line.set_value(ctx);
        ctx.stroke();
        ctx.restore();
    };
    BoxAnnotationView.prototype.interactive_bbox = function () {
        var tol = this.model.properties.line_width.value() + exports.EDGE_TOLERANCE;
        return new bbox_1.BBox({
            x0: this.sleft - tol,
            y0: this.stop - tol,
            x1: this.sright + tol,
            y1: this.sbottom + tol,
        });
    };
    BoxAnnotationView.prototype.interactive_hit = function (sx, sy) {
        if (this.model.in_cursor == null)
            return false;
        var bbox = this.interactive_bbox();
        return bbox.contains(sx, sy);
    };
    BoxAnnotationView.prototype.cursor = function (sx, sy) {
        var tol = 3;
        if (Math.abs(sx - this.sleft) < tol || Math.abs(sx - this.sright) < tol)
            return this.model.ew_cursor;
        else if (Math.abs(sy - this.sbottom) < tol || Math.abs(sy - this.stop) < tol)
            return this.model.ns_cursor;
        else if (sx > this.sleft && sx < this.sright && sy > this.stop && sy < this.sbottom)
            return this.model.in_cursor;
        else
            return null;
    };
    return BoxAnnotationView;
}(annotation_1.AnnotationView));
exports.BoxAnnotationView = BoxAnnotationView;
var BoxAnnotation = /** @class */ (function (_super) {
    tslib_1.__extends(BoxAnnotation, _super);
    function BoxAnnotation(attrs) {
        return _super.call(this, attrs) || this;
    }
    BoxAnnotation.initClass = function () {
        this.prototype.type = 'BoxAnnotation';
        this.prototype.default_view = BoxAnnotationView;
        this.mixins(['line', 'fill']);
        this.define({
            render_mode: [p.RenderMode, 'canvas'],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
            top: [p.Number, null],
            top_units: [p.SpatialUnits, 'data'],
            bottom: [p.Number, null],
            bottom_units: [p.SpatialUnits, 'data'],
            left: [p.Number, null],
            left_units: [p.SpatialUnits, 'data'],
            right: [p.Number, null],
            right_units: [p.SpatialUnits, 'data'],
        });
        this.internal({
            screen: [p.Boolean, false],
            ew_cursor: [p.String, null],
            ns_cursor: [p.String, null],
            in_cursor: [p.String, null],
        });
        this.override({
            fill_color: '#fff9ba',
            fill_alpha: 0.4,
            line_color: '#cccccc',
            line_alpha: 0.3,
        });
    };
    BoxAnnotation.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.data_update = new signaling_1.Signal0(this, "data_update");
    };
    BoxAnnotation.prototype.update = function (_a) {
        var left = _a.left, right = _a.right, top = _a.top, bottom = _a.bottom;
        this.setv({ left: left, right: right, top: top, bottom: bottom, screen: true }, { silent: true });
        this.data_update.emit();
    };
    return BoxAnnotation;
}(annotation_1.Annotation));
exports.BoxAnnotation = BoxAnnotation;
BoxAnnotation.initClass();
