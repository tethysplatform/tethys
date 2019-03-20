"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var arrow_head_1 = require("./arrow_head");
var column_data_source_1 = require("../sources/column_data_source");
var p = require("core/properties");
var math_1 = require("core/util/math");
var ArrowView = /** @class */ (function (_super) {
    tslib_1.__extends(ArrowView, _super);
    function ArrowView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ArrowView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        if (this.model.source == null)
            this.model.source = new column_data_source_1.ColumnDataSource();
        this.set_data(this.model.source);
    };
    ArrowView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.plot_view.request_render(); });
        this.connect(this.model.source.streaming, function () { return _this.set_data(_this.model.source); });
        this.connect(this.model.source.patching, function () { return _this.set_data(_this.model.source); });
        this.connect(this.model.source.change, function () { return _this.set_data(_this.model.source); });
    };
    ArrowView.prototype.set_data = function (source) {
        _super.prototype.set_data.call(this, source);
        this.visuals.warm_cache(source);
        this.plot_view.request_render();
    };
    ArrowView.prototype._map_data = function () {
        var frame = this.plot_view.frame;
        var sx_start, sy_start;
        if (this.model.start_units == 'data') {
            sx_start = frame.xscales[this.model.x_range_name].v_compute(this._x_start);
            sy_start = frame.yscales[this.model.y_range_name].v_compute(this._y_start);
        }
        else {
            sx_start = frame.xview.v_compute(this._x_start);
            sy_start = frame.yview.v_compute(this._y_start);
        }
        var sx_end, sy_end;
        if (this.model.end_units == 'data') {
            sx_end = frame.xscales[this.model.x_range_name].v_compute(this._x_end);
            sy_end = frame.yscales[this.model.y_range_name].v_compute(this._y_end);
        }
        else {
            sx_end = frame.xview.v_compute(this._x_end);
            sy_end = frame.yview.v_compute(this._y_end);
        }
        return [[sx_start, sy_start], [sx_end, sy_end]];
    };
    ArrowView.prototype.render = function () {
        if (!this.model.visible)
            return;
        var ctx = this.plot_view.canvas_view.ctx;
        ctx.save();
        // Order in this function is important. First we draw all the arrow heads.
        var _a = this._map_data(), start = _a[0], end = _a[1];
        if (this.model.end != null)
            this._arrow_head(ctx, "render", this.model.end, start, end);
        if (this.model.start != null)
            this._arrow_head(ctx, "render", this.model.start, end, start);
        // Next we call .clip on all the arrow heads, inside an initial canvas sized
        // rect, to create an "inverted" clip region for the arrow heads
        ctx.beginPath();
        var _b = this.plot_model.canvas.bbox.rect, x = _b.x, y = _b.y, width = _b.width, height = _b.height;
        ctx.rect(x, y, width, height);
        if (this.model.end != null)
            this._arrow_head(ctx, "clip", this.model.end, start, end);
        if (this.model.start != null)
            this._arrow_head(ctx, "clip", this.model.start, end, start);
        ctx.closePath();
        ctx.clip();
        // Finally we draw the arrow body, with the clipping regions set up. This prevents
        // "fat" arrows from overlapping the arrow head in a bad way.
        this._arrow_body(ctx, start, end);
        ctx.restore();
    };
    ArrowView.prototype._arrow_head = function (ctx, action, head, start, end) {
        for (var i = 0, _end = this._x_start.length; i < _end; i++) {
            // arrow head runs orthogonal to arrow body
            var angle = Math.PI / 2 + math_1.atan2([start[0][i], start[1][i]], [end[0][i], end[1][i]]);
            ctx.save();
            ctx.translate(end[0][i], end[1][i]);
            ctx.rotate(angle);
            if (action == "render")
                head.render(ctx, i);
            else if (action == "clip")
                head.clip(ctx, i);
            ctx.restore();
        }
    };
    ArrowView.prototype._arrow_body = function (ctx, start, end) {
        if (!this.visuals.line.doit)
            return;
        for (var i = 0, n = this._x_start.length; i < n; i++) {
            this.visuals.line.set_vectorize(ctx, i);
            ctx.beginPath();
            ctx.moveTo(start[0][i], start[1][i]);
            ctx.lineTo(end[0][i], end[1][i]);
            ctx.stroke();
        }
    };
    return ArrowView;
}(annotation_1.AnnotationView));
exports.ArrowView = ArrowView;
var Arrow = /** @class */ (function (_super) {
    tslib_1.__extends(Arrow, _super);
    function Arrow(attrs) {
        return _super.call(this, attrs) || this;
    }
    Arrow.initClass = function () {
        this.prototype.type = 'Arrow';
        this.prototype.default_view = ArrowView;
        this.mixins(['line']);
        this.define({
            x_start: [p.NumberSpec,],
            y_start: [p.NumberSpec,],
            start_units: [p.String, 'data'],
            start: [p.Instance, null],
            x_end: [p.NumberSpec,],
            y_end: [p.NumberSpec,],
            end_units: [p.String, 'data'],
            end: [p.Instance, function () { return new arrow_head_1.OpenHead({}); }],
            source: [p.Instance],
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
        });
    };
    return Arrow;
}(annotation_1.Annotation));
exports.Arrow = Arrow;
Arrow.initClass();
