"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var numbro = require("numbro");
var abstract_slider_1 = require("./abstract_slider");
var RangeSliderView = /** @class */ (function (_super) {
    tslib_1.__extends(RangeSliderView, _super);
    function RangeSliderView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RangeSliderView.prototype._calc_to = function () {
        return {
            start: this.model.start,
            end: this.model.end,
            value: this.model.value,
            step: this.model.step,
        };
    };
    RangeSliderView.prototype._calc_from = function (values) {
        return values;
    };
    return RangeSliderView;
}(abstract_slider_1.AbstractSliderView));
exports.RangeSliderView = RangeSliderView;
var RangeSlider = /** @class */ (function (_super) {
    tslib_1.__extends(RangeSlider, _super);
    function RangeSlider(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.behaviour = "drag";
        _this.connected = [false, true, false];
        return _this;
    }
    RangeSlider.initClass = function () {
        this.prototype.type = "RangeSlider";
        this.prototype.default_view = RangeSliderView;
        this.override({
            format: "0[.]00",
        });
    };
    RangeSlider.prototype._formatter = function (value, format) {
        return numbro.format(value, format);
    };
    return RangeSlider;
}(abstract_slider_1.AbstractSlider));
exports.RangeSlider = RangeSlider;
RangeSlider.initClass();
