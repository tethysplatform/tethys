"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var tz = require("timezone");
var abstract_slider_1 = require("./abstract_slider");
var DateSliderView = /** @class */ (function (_super) {
    tslib_1.__extends(DateSliderView, _super);
    function DateSliderView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DateSliderView.prototype._calc_to = function () {
        return {
            start: this.model.start,
            end: this.model.end,
            value: [this.model.value],
            step: this.model.step,
        };
    };
    DateSliderView.prototype._calc_from = function (_a) {
        var value = _a[0];
        return value;
    };
    return DateSliderView;
}(abstract_slider_1.AbstractSliderView));
exports.DateSliderView = DateSliderView;
var DateSlider = /** @class */ (function (_super) {
    tslib_1.__extends(DateSlider, _super);
    function DateSlider(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.behaviour = "tap";
        _this.connected = [true, false];
        return _this;
    }
    DateSlider.initClass = function () {
        this.prototype.type = "DateSlider";
        this.prototype.default_view = DateSliderView;
        this.override({
            format: "%d %b %Y",
        });
    };
    DateSlider.prototype._formatter = function (value, format) {
        return tz(value, format);
    };
    return DateSlider;
}(abstract_slider_1.AbstractSlider));
exports.DateSlider = DateSlider;
DateSlider.initClass();
