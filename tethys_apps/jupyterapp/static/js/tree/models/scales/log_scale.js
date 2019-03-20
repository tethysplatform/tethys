"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var scale_1 = require("./scale");
var LogScale = /** @class */ (function (_super) {
    tslib_1.__extends(LogScale, _super);
    function LogScale(attrs) {
        return _super.call(this, attrs) || this;
    }
    LogScale.initClass = function () {
        this.prototype.type = "LogScale";
    };
    LogScale.prototype.compute = function (x) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1], inter_factor = _a[2], inter_offset = _a[3];
        var value;
        if (inter_factor == 0)
            value = 0;
        else {
            var _x = (Math.log(x) - inter_offset) / inter_factor;
            if (isFinite(_x))
                value = _x * factor + offset;
            else
                value = NaN;
        }
        return value;
    };
    LogScale.prototype.v_compute = function (xs) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1], inter_factor = _a[2], inter_offset = _a[3];
        var result = new Float64Array(xs.length);
        if (inter_factor == 0) {
            for (var i = 0; i < xs.length; i++)
                result[i] = 0;
        }
        else {
            for (var i = 0; i < xs.length; i++) {
                var _x = (Math.log(xs[i]) - inter_offset) / inter_factor;
                var value = void 0;
                if (isFinite(_x))
                    value = _x * factor + offset;
                else
                    value = NaN;
                result[i] = value;
            }
        }
        return result;
    };
    LogScale.prototype.invert = function (xprime) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1], inter_factor = _a[2], inter_offset = _a[3];
        var value = (xprime - offset) / factor;
        return Math.exp(inter_factor * value + inter_offset);
    };
    LogScale.prototype.v_invert = function (xprimes) {
        var _a = this._compute_state(), factor = _a[0], offset = _a[1], inter_factor = _a[2], inter_offset = _a[3];
        var result = new Float64Array(xprimes.length);
        for (var i = 0; i < xprimes.length; i++) {
            var value = (xprimes[i] - offset) / factor;
            result[i] = Math.exp(inter_factor * value + inter_offset);
        }
        return result;
    };
    LogScale.prototype._get_safe_factor = function (orig_start, orig_end) {
        var _a;
        var start = orig_start < 0 ? 0 : orig_start;
        var end = orig_end < 0 ? 0 : orig_end;
        if (start == end) {
            if (start == 0)
                _a = [1, 10], start = _a[0], end = _a[1];
            else {
                var log_val = Math.log(start) / Math.log(10);
                start = Math.pow(10, Math.floor(log_val));
                if (Math.ceil(log_val) != Math.floor(log_val))
                    end = Math.pow(10, Math.ceil(log_val));
                else
                    end = Math.pow(10, Math.ceil(log_val) + 1);
            }
        }
        return [start, end];
    };
    LogScale.prototype._compute_state = function () {
        var source_start = this.source_range.start;
        var source_end = this.source_range.end;
        var target_start = this.target_range.start;
        var target_end = this.target_range.end;
        var screen_range = target_end - target_start;
        var _a = this._get_safe_factor(source_start, source_end), start = _a[0], end = _a[1];
        var inter_factor;
        var inter_offset;
        if (start == 0) {
            inter_factor = Math.log(end);
            inter_offset = 0;
        }
        else {
            inter_factor = Math.log(end) - Math.log(start);
            inter_offset = Math.log(start);
        }
        var factor = screen_range;
        var offset = target_start;
        return [factor, offset, inter_factor, inter_offset];
    };
    return LogScale;
}(scale_1.Scale));
exports.LogScale = LogScale;
LogScale.initClass();
