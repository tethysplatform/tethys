"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tz = require("timezone");
var abstract_slider_1 = require("./abstract_slider");
var DateRangeSliderView = /** @class */ (function (_super) {
    tslib_1.__extends(DateRangeSliderView, _super);
    function DateRangeSliderView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DateRangeSliderView.prototype._calc_to = function () {
        return {
            start: this.model.start,
            end: this.model.end,
            value: this.model.value,
            step: this.model.step,
        };
    };
    DateRangeSliderView.prototype._calc_from = function (values) {
        return values;
    };
    return DateRangeSliderView;
}(abstract_slider_1.AbstractSliderView));
exports.DateRangeSliderView = DateRangeSliderView;
var DateRangeSlider = /** @class */ (function (_super) {
    tslib_1.__extends(DateRangeSlider, _super);
    function DateRangeSlider(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.behaviour = "drag";
        _this.connected = [false, true, false];
        return _this;
    }
    DateRangeSlider.initClass = function () {
        this.prototype.type = "DateRangeSlider";
        this.prototype.default_view = DateRangeSliderView;
        this.override({
            format: "%d %b %Y",
        });
    };
    DateRangeSlider.prototype._formatter = function (value, format) {
        return tz(value, format);
    };
    return DateRangeSlider;
}(abstract_slider_1.AbstractSlider));
exports.DateRangeSlider = DateRangeSlider;
DateRangeSlider.initClass();
