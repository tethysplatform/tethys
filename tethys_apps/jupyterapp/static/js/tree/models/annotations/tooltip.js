"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var dom_1 = require("core/dom");
var p = require("core/properties");
function compute_side(attachment, sx, sy, hcenter, vcenter) {
    var side;
    switch (attachment) {
        case "horizontal":
            side = sx < hcenter ? 'right' : 'left';
            break;
        case "vertical":
            side = sy < vcenter ? 'below' : 'above';
            break;
        default:
            side = attachment;
    }
    return side;
}
exports.compute_side = compute_side;
var TooltipView = /** @class */ (function (_super) {
    tslib_1.__extends(TooltipView, _super);
    function TooltipView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TooltipView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        // TODO (bev) really probably need multiple divs
        this.plot_view.canvas_overlays.appendChild(this.el);
        dom_1.hide(this.el);
    };
    TooltipView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.data.change, function () { return _this._draw_tips(); });
    };
    TooltipView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-tooltip");
    };
    TooltipView.prototype.render = function () {
        if (!this.model.visible)
            return;
        this._draw_tips();
    };
    TooltipView.prototype._draw_tips = function () {
        var data = this.model.data;
        dom_1.empty(this.el);
        dom_1.hide(this.el);
        if (this.model.custom)
            this.el.classList.add("bk-tooltip-custom");
        else
            this.el.classList.remove("bk-tooltip-custom");
        if (data.length == 0)
            return;
        var frame = this.plot_view.frame;
        for (var _i = 0, data_1 = data; _i < data_1.length; _i++) {
            var _a = data_1[_i], sx_1 = _a[0], sy_1 = _a[1], content = _a[2];
            if (this.model.inner_only && !frame.bbox.contains(sx_1, sy_1))
                continue;
            var tip = dom_1.div({}, content);
            this.el.appendChild(tip);
        }
        var _b = data[data.length - 1], sx = _b[0], sy = _b[1]; // XXX: this previously depended on {sx, sy} leaking from the for-loop
        var side = compute_side(this.model.attachment, sx, sy, frame._hcenter.value, frame._vcenter.value);
        this.el.classList.remove("bk-right");
        this.el.classList.remove("bk-left");
        this.el.classList.remove("bk-above");
        this.el.classList.remove("bk-below");
        var arrow_size = 10; // XXX: keep in sync with less
        dom_1.show(this.el); // XXX: {offset,client}Width() gives 0 when display="none"
        // slightly confusing: side "left" (for example) is relative to point that
        // is being annotated but CS class "bk-left" is relative to the tooltip itself
        var left, top;
        switch (side) {
            case "right":
                this.el.classList.add("bk-left");
                left = sx + (this.el.offsetWidth - this.el.clientWidth) + arrow_size;
                top = sy - this.el.offsetHeight / 2;
                break;
            case "left":
                this.el.classList.add("bk-right");
                left = sx - this.el.offsetWidth - arrow_size;
                top = sy - this.el.offsetHeight / 2;
                break;
            case "below":
                this.el.classList.add("bk-above");
                top = sy + (this.el.offsetHeight - this.el.clientHeight) + arrow_size;
                left = Math.round(sx - this.el.offsetWidth / 2);
                break;
            case "above":
                this.el.classList.add("bk-below");
                top = sy - this.el.offsetHeight - arrow_size;
                left = Math.round(sx - this.el.offsetWidth / 2);
                break;
            default:
                throw new Error("unreachable code");
        }
        if (this.model.show_arrow)
            this.el.classList.add("bk-tooltip-arrow");
        // TODO (bev) this is not currently bulletproof. If there are
        // two hits, not colocated and one is off the screen, that can
        // be problematic
        if (this.el.childNodes.length > 0) {
            this.el.style.top = top + "px";
            this.el.style.left = left + "px";
        }
        else
            dom_1.hide(this.el);
    };
    return TooltipView;
}(annotation_1.AnnotationView));
exports.TooltipView = TooltipView;
var Tooltip = /** @class */ (function (_super) {
    tslib_1.__extends(Tooltip, _super);
    function Tooltip(attrs) {
        return _super.call(this, attrs) || this;
    }
    Tooltip.initClass = function () {
        this.prototype.type = 'Tooltip';
        this.prototype.default_view = TooltipView;
        this.define({
            attachment: [p.String, 'horizontal'],
            inner_only: [p.Bool, true],
            show_arrow: [p.Bool, true],
        });
        this.override({
            level: 'overlay',
        });
        this.internal({
            data: [p.Any, []],
            custom: [p.Any],
        });
    };
    Tooltip.prototype.clear = function () {
        this.data = [];
    };
    Tooltip.prototype.add = function (sx, sy, content) {
        this.data = this.data.concat([[sx, sy, content]]);
    };
    return Tooltip;
}(annotation_1.Annotation));
exports.Tooltip = Tooltip;
Tooltip.initClass();
