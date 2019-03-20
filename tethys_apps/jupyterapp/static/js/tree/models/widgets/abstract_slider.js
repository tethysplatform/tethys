"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var noUiSlider = require("nouislider");
var p = require("core/properties");
var dom_1 = require("core/dom");
var logging_1 = require("core/logging");
var array_1 = require("core/util/array");
var callback_1 = require("core/util/callback");
var widget_1 = require("./widget");
var AbstractSliderView = /** @class */ (function (_super) {
    tslib_1.__extends(AbstractSliderView, _super);
    function AbstractSliderView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AbstractSliderView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.render();
    };
    AbstractSliderView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.change, function () { return _this.render(); });
    };
    AbstractSliderView.prototype.render = function () {
        var _this = this;
        if (this.sliderEl == null) {
            // XXX: temporary workaround for _render_css()
            _super.prototype.render.call(this);
        }
        if (this.model.callback != null) {
            var callback = function () { return _this.model.callback.execute(_this.model); };
            switch (this.model.callback_policy) {
                case 'continuous': {
                    this.callback_wrapper = callback;
                    break;
                }
                case 'throttle': {
                    this.callback_wrapper = callback_1.throttle(callback, this.model.callback_throttle);
                    break;
                }
            }
        }
        var prefix = 'bk-noUi-';
        var _a = this._calc_to(), start = _a.start, end = _a.end, value = _a.value, step = _a.step;
        var tooltips; // XXX
        if (this.model.tooltips) {
            var formatter = {
                to: function (value) { return _this.model.pretty(value); },
            };
            tooltips = array_1.repeat(formatter, value.length);
        }
        else
            tooltips = false;
        this.el.classList.add("bk-slider");
        if (this.sliderEl == null) {
            this.sliderEl = dom_1.div();
            this.el.appendChild(this.sliderEl);
            noUiSlider.create(this.sliderEl, {
                cssPrefix: prefix,
                range: { min: start, max: end },
                start: value,
                step: step,
                behaviour: this.model.behaviour,
                connect: this.model.connected,
                tooltips: tooltips,
                orientation: this.model.orientation,
                direction: this.model.direction,
            }); // XXX: bad typings; no cssPrefix
            this.sliderEl.noUiSlider.on('slide', function (_, __, values) { return _this._slide(values); });
            this.sliderEl.noUiSlider.on('change', function (_, __, values) { return _this._change(values); });
            // Add keyboard support
            var keypress = function (e) {
                var spec = _this._calc_to();
                var value = spec.value[0];
                switch (e.which) {
                    case 37: {
                        value = Math.max(value - step, start);
                        break;
                    }
                    case 39: {
                        value = Math.min(value + step, end);
                        break;
                    }
                    default:
                        return;
                }
                var pretty = _this.model.pretty(value);
                logging_1.logger.debug("[slider keypress] value = " + pretty);
                _this.model.value = value;
                _this.sliderEl.noUiSlider.set(value);
                if (_this.valueEl != null)
                    _this.valueEl.textContent = pretty;
                if (_this.callback_wrapper != null)
                    _this.callback_wrapper();
            };
            var handle = this.sliderEl.querySelector("." + prefix + "handle");
            handle.setAttribute('tabindex', '0');
            handle.addEventListener('keydown', keypress);
            var toggleTooltip_1 = function (i, show) {
                var handle = _this.sliderEl.querySelectorAll("." + prefix + "handle")[i];
                var tooltip = handle.querySelector("." + prefix + "tooltip");
                tooltip.style.display = show ? 'block' : '';
            };
            this.sliderEl.noUiSlider.on('start', function (_, i) { return toggleTooltip_1(i, true); });
            this.sliderEl.noUiSlider.on('end', function (_, i) { return toggleTooltip_1(i, false); });
        }
        else {
            this.sliderEl.noUiSlider.updateOptions({
                range: { min: start, max: end },
                start: value,
                step: step,
            });
        }
        if (this.titleEl != null)
            this.el.removeChild(this.titleEl);
        if (this.valueEl != null)
            this.el.removeChild(this.valueEl);
        if (this.model.title != null) {
            if (this.model.title.length != 0) {
                this.titleEl = dom_1.label({}, this.model.title + ":");
                this.el.insertBefore(this.titleEl, this.sliderEl);
            }
            if (this.model.show_value) {
                var pretty = value.map(function (v) { return _this.model.pretty(v); }).join(" .. ");
                this.valueEl = dom_1.div({ class: "bk-slider-value" }, pretty);
                this.el.insertBefore(this.valueEl, this.sliderEl);
            }
        }
        if (!this.model.disabled) {
            this.sliderEl.querySelector("." + prefix + "connect")
                .style
                .backgroundColor = this.model.bar_color;
        }
        if (this.model.disabled)
            this.sliderEl.setAttribute('disabled', 'true');
        else
            this.sliderEl.removeAttribute('disabled');
    };
    AbstractSliderView.prototype._slide = function (values) {
        var _this = this;
        var value = this._calc_from(values);
        var pretty = values.map(function (v) { return _this.model.pretty(v); }).join(" .. ");
        logging_1.logger.debug("[slider slide] value = " + pretty);
        if (this.valueEl != null)
            this.valueEl.textContent = pretty;
        this.model.value = value;
        if (this.callback_wrapper != null)
            this.callback_wrapper();
    };
    AbstractSliderView.prototype._change = function (values) {
        var _this = this;
        var value = this._calc_from(values);
        var pretty = values.map(function (v) { return _this.model.pretty(v); }).join(" .. ");
        logging_1.logger.debug("[slider change] value = " + pretty);
        if (this.valueEl != null)
            this.valueEl.dataset.value = pretty;
        this.model.value = value;
        switch (this.model.callback_policy) {
            case 'mouseup':
            case 'throttle': {
                if (this.model.callback != null)
                    this.model.callback.execute(this.model);
                break;
            }
        }
    };
    return AbstractSliderView;
}(widget_1.WidgetView));
exports.AbstractSliderView = AbstractSliderView;
var AbstractSlider = /** @class */ (function (_super) {
    tslib_1.__extends(AbstractSlider, _super);
    function AbstractSlider(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.connected = false;
        return _this;
    }
    AbstractSlider.initClass = function () {
        this.prototype.type = "AbstractSlider";
        this.define({
            title: [p.String, ""],
            show_value: [p.Bool, true],
            start: [p.Any],
            end: [p.Any],
            value: [p.Any],
            step: [p.Number, 1],
            format: [p.String],
            orientation: [p.Orientation, "horizontal"],
            direction: [p.Any, "ltr"],
            tooltips: [p.Boolean, true],
            callback: [p.Instance],
            callback_throttle: [p.Number, 200],
            callback_policy: [p.String, "throttle"],
            bar_color: [p.Color, "#e6e6e6"],
        });
    };
    AbstractSlider.prototype._formatter = function (value, _format) {
        return "" + value;
    };
    AbstractSlider.prototype.pretty = function (value) {
        return this._formatter(value, this.format);
    };
    return AbstractSlider;
}(widget_1.Widget));
exports.AbstractSlider = AbstractSlider;
AbstractSlider.initClass();
