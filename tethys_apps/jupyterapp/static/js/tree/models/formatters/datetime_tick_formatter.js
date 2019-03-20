"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var sprintf_js_1 = require("sprintf-js");
var tz = require("timezone");
var tick_formatter_1 = require("./tick_formatter");
var logging_1 = require("core/logging");
var p = require("core/properties");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
function _us(t) {
    // From double-precision unix (millisecond) timestamp get
    // microsecond since last second. Precision seems to run
    // out around the hundreds of nanoseconds scale, so rounding
    // to the nearest microsecond should round to a nice
    // microsecond / millisecond tick.
    return Math.round(((t / 1000) % 1) * 1000000);
}
function _array(t) {
    return tz(t, "%Y %m %d %H %M %S").split(/\s+/).map(function (e) { return parseInt(e, 10); });
}
function _strftime(t, format) {
    if (types_1.isFunction(format)) {
        return format(t);
    }
    else {
        // Python's datetime library augments the microsecond directive %f, which is not
        // supported by the javascript library timezone: http://bigeasy.github.io/timezone/.
        // Use a regular expression to replace %f directive with microseconds.
        // TODO: what should we do for negative microsecond strings?
        var microsecond_replacement_string = sprintf_js_1.sprintf("$1%06d", _us(t));
        format = format.replace(/((^|[^%])(%%)*)%f/, microsecond_replacement_string);
        if (format.indexOf("%") == -1) {
            // timezone seems to ignore any strings without any formatting directives,
            // and just return the time argument back instead of the string argument.
            // But we want the string argument, in case a user supplies a format string
            // which doesn't contain a formatting directive or is only using %f.
            return format;
        }
        return tz(t, format);
    }
}
// Labels of time units, from finest to coarsest.
var format_order = [
    'microseconds', 'milliseconds', 'seconds', 'minsec', 'minutes', 'hourmin', 'hours', 'days', 'months', 'years',
];
var DatetimeTickFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(DatetimeTickFormatter, _super);
    function DatetimeTickFormatter(attrs) {
        var _this = _super.call(this, attrs) || this;
        // Whether or not to strip the leading zeros on tick labels.
        _this.strip_leading_zeros = true;
        return _this;
    }
    DatetimeTickFormatter.initClass = function () {
        this.prototype.type = 'DatetimeTickFormatter';
        this.define({
            microseconds: [p.Array, ['%fus']],
            milliseconds: [p.Array, ['%3Nms', '%S.%3Ns']],
            seconds: [p.Array, ['%Ss']],
            minsec: [p.Array, [':%M:%S']],
            minutes: [p.Array, [':%M', '%Mm']],
            hourmin: [p.Array, ['%H:%M']],
            hours: [p.Array, ['%Hh', '%H:%M']],
            days: [p.Array, ['%m/%d', '%a%d']],
            months: [p.Array, ['%m/%Y', '%b %Y']],
            years: [p.Array, ['%Y']],
        });
    };
    DatetimeTickFormatter.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        // TODO (bev) trigger update on format change
        this._update_width_formats();
    };
    DatetimeTickFormatter.prototype._update_width_formats = function () {
        var now = +tz(new Date());
        var _widths = function (fmt_strings) {
            var sizes = fmt_strings.map(function (fmt_string) { return _strftime(now, fmt_string).length; });
            var sorted = array_1.sortBy(array_1.zip(sizes, fmt_strings), function (_a) {
                var size = _a[0];
                return size;
            });
            return array_1.unzip(sorted);
        };
        this._width_formats = {
            microseconds: _widths(this.microseconds),
            milliseconds: _widths(this.milliseconds),
            seconds: _widths(this.seconds),
            minsec: _widths(this.minsec),
            minutes: _widths(this.minutes),
            hourmin: _widths(this.hourmin),
            hours: _widths(this.hours),
            days: _widths(this.days),
            months: _widths(this.months),
            years: _widths(this.years),
        };
    };
    // FIXME There is some unfortunate flicker when panning/zooming near the
    // span boundaries.
    // FIXME Rounding is weird at the 20-us scale and below.
    DatetimeTickFormatter.prototype._get_resolution_str = function (resolution_secs, span_secs) {
        // Our resolution boundaries should not be round numbers, because we want
        // them to fall between the possible tick intervals (which *are* round
        // numbers, as we've worked hard to ensure).  Consequently, we adjust the
        // resolution upwards a small amount (less than any possible step in
        // scales) to make the effective boundaries slightly lower.
        var adjusted_secs = resolution_secs * 1.1;
        switch (false) {
            case !(adjusted_secs < 1e-3): return "microseconds";
            case !(adjusted_secs < 1.0): return "milliseconds";
            case !(adjusted_secs < 60): return span_secs >= 60 ? "minsec" : "seconds";
            case !(adjusted_secs < 3600): return span_secs >= 3600 ? "hourmin" : "minutes";
            case !(adjusted_secs < (24 * 3600)): return "hours";
            case !(adjusted_secs < (31 * 24 * 3600)): return "days";
            case !(adjusted_secs < (365 * 24 * 3600)): return "months";
            default: return "years";
        }
    };
    DatetimeTickFormatter.prototype.doFormat = function (ticks, _axis) {
        // In order to pick the right set of labels, we need to determine
        // the resolution of the ticks.  We can do this using a ticker if
        // it's provided, or by computing the resolution from the actual
        // ticks we've been given.
        if (ticks.length == 0)
            return [];
        var span = Math.abs(ticks[ticks.length - 1] - ticks[0]) / 1000.0;
        var r = span / (ticks.length - 1);
        var resol = this._get_resolution_str(r, span);
        var _a = this._width_formats[resol], format = _a[1][0];
        // Apply the format to the tick values
        var labels = [];
        var resol_ndx = format_order.indexOf(resol);
        // This dictionary maps the name of a time resolution (in @format_order)
        // to its index in a time.localtime() timetuple.  The default is to map
        // everything to index 0, which is year.  This is not ideal; it might cause
        // a problem with the tick at midnight, january 1st, 0 a.d. being incorrectly
        // promoted at certain tick resolutions.
        var time_tuple_ndx_for_resol = {};
        for (var _i = 0, format_order_1 = format_order; _i < format_order_1.length; _i++) {
            var fmt = format_order_1[_i];
            time_tuple_ndx_for_resol[fmt] = 0;
        }
        time_tuple_ndx_for_resol["seconds"] = 5;
        time_tuple_ndx_for_resol["minsec"] = 4;
        time_tuple_ndx_for_resol["minutes"] = 4;
        time_tuple_ndx_for_resol["hourmin"] = 3;
        time_tuple_ndx_for_resol["hours"] = 3;
        // As we format each tick, check to see if we are at a boundary of the
        // next higher unit of time.  If so, replace the current format with one
        // from that resolution.  This is not the best heuristic in the world,
        // but it works!  There is some trickiness here due to having to deal
        // with hybrid formats in a reasonable manner.
        for (var _b = 0, ticks_1 = ticks; _b < ticks_1.length; _b++) {
            var t = ticks_1[_b];
            var s = void 0, tm = void 0;
            try {
                tm = _array(t);
                s = _strftime(t, format);
            }
            catch (error) {
                logging_1.logger.warn("unable to format tick for timestamp value " + t);
                logging_1.logger.warn(" - " + error);
                labels.push("ERR");
                continue;
            }
            var hybrid_handled = false;
            var next_ndx = resol_ndx;
            // The way to check that we are at the boundary of the next unit of
            // time is by checking that we have 0 units of the resolution, i.e.
            // we are at zero minutes, so display hours, or we are at zero seconds,
            // so display minutes (and if that is zero as well, then display hours).
            while (tm[time_tuple_ndx_for_resol[format_order[next_ndx]]] == 0) {
                var next_format = void 0;
                next_ndx += 1;
                if (next_ndx == format_order.length)
                    break;
                if ((resol == "minsec" || resol == "hourmin") && !hybrid_handled) {
                    if ((resol == "minsec" && tm[4] == 0 && tm[5] != 0) || (resol == "hourmin" && tm[3] == 0 && tm[4] != 0)) {
                        next_format = this._width_formats[format_order[resol_ndx - 1]][1][0];
                        s = _strftime(t, next_format);
                        break;
                    }
                    else {
                        hybrid_handled = true;
                    }
                }
                next_format = this._width_formats[format_order[next_ndx]][1][0];
                s = _strftime(t, next_format);
            }
            // TODO: should expose this in api. %H, %d, etc use leading zeros and
            // users might prefer to see them lined up correctly.
            if (this.strip_leading_zeros) {
                var ss = s.replace(/^0+/g, "");
                if (ss != s && isNaN(parseInt(ss))) {
                    // If the string can now be parsed as starting with an integer, then
                    // leave all zeros stripped, otherwise start with a zero. Hence:
                    // A label such as '000ms' should leave one zero.
                    // A label such as '001ms' or '0-1ms' should not leave a leading zero.
                    ss = "0" + ss;
                }
                labels.push(ss);
            }
            else
                labels.push(s);
        }
        return labels;
    };
    return DatetimeTickFormatter;
}(tick_formatter_1.TickFormatter));
exports.DatetimeTickFormatter = DatetimeTickFormatter;
DatetimeTickFormatter.initClass();
