"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var sprintf_js_1 = require("sprintf-js");
var Numbro = require("numbro");
var tz = require("timezone");
var string_1 = require("./string");
var types_1 = require("./types");
exports.DEFAULT_FORMATTERS = {
    numeral: function (value, format, _special_vars) { return Numbro.format(value, format); },
    datetime: function (value, format, _special_vars) { return tz(value, format); },
    printf: function (value, format, _special_vars) { return sprintf_js_1.sprintf(format, value); },
};
function basic_formatter(value, _format, _special_vars) {
    if (types_1.isNumber(value)) {
        var format = (function () {
            switch (false) {
                case Math.floor(value) != value:
                    return "%d";
                case !(Math.abs(value) > 0.1) || !(Math.abs(value) < 1000):
                    return "%0.3f";
                default:
                    return "%0.3e";
            }
        })();
        return sprintf_js_1.sprintf(format, value);
    }
    else
        return "" + value; // get strings for categorical types
}
exports.basic_formatter = basic_formatter;
function get_formatter(name, raw_spec, format, formatters) {
    // no format, use default built in formatter
    if (format == null)
        return basic_formatter;
    // format spec in the formatters dict, use that
    if (formatters != null && (name in formatters || raw_spec in formatters)) {
        // some day (Bokeh 2.0) we can get rid of the check for name, and just check the raw spec
        // keep it now for compatibility but do not demonstrate it anywhere
        var key = raw_spec in formatters ? raw_spec : name;
        var formatter_1 = formatters[key];
        if (types_1.isString(formatter_1)) {
            if (formatter_1 in exports.DEFAULT_FORMATTERS)
                return exports.DEFAULT_FORMATTERS[formatter_1];
            else
                throw new Error("Unknown tooltip field formatter type '" + formatter_1 + "'");
        }
        return function (value, format, special_vars) {
            return formatter_1.format(value, format, special_vars);
        };
    }
    // otherwise use "numeral" as default
    return exports.DEFAULT_FORMATTERS["numeral"];
}
exports.get_formatter = get_formatter;
function get_value(name, data_source, i, special_vars) {
    if (name[0] == "$") {
        if (name.substring(1) in special_vars)
            return special_vars[name.substring(1)];
        else
            throw new Error("Unknown special variable '" + name + "'");
    }
    var column = data_source.get_column(name);
    // missing column
    if (column == null)
        return null;
    // typical (non-image) index
    if (types_1.isNumber(i))
        return column[i];
    // image index
    var data = column[i.index];
    if (types_1.isTypedArray(data) || types_1.isArray(data)) {
        // inspect array of arrays
        if (types_1.isArray(data[0])) {
            var row = data[i.dim2];
            return row[i.dim1];
        }
        // inspect flat array
        else
            return data[i.flat_index];
    }
    // inspect per-image scalar data
    else
        return data;
}
exports.get_value = get_value;
function replace_placeholders(str, data_source, i, formatters, special_vars) {
    if (special_vars === void 0) { special_vars = {}; }
    // this extracts the $x, @x, @{x} without any trailing {format}
    var raw_spec = str.replace(/(?:^|[^@])([@|\$](?:\w+|{[^{}]+}))(?:{[^{}]+})?/g, function (_match, raw_spec, _format) { return "" + raw_spec; });
    // this handles the special case @$name, replacing it with an @var corresponding to special_vars.name
    str = str.replace(/@\$name/g, function (_match) { return "@{" + special_vars.name + "}"; });
    // this prepends special vars with "@", e.g "$x" becomes "@$x", so subsequent processing is simpler
    str = str.replace(/(^|[^\$])\$(\w+)/g, function (_match, prefix, name) { return prefix + "@$" + name; });
    str = str.replace(/(^|[^@])@(?:(\$?\w+)|{([^{}]+)})(?:{([^{}]+)})?/g, function (_match, prefix, name, long_name, format) {
        name = long_name != null ? long_name : name;
        var value = get_value(name, data_source, i, special_vars);
        // missing value, return ???
        if (value == null)
            return "" + prefix + string_1.escape("???");
        // 'safe' format, return the value as-is
        if (format == 'safe')
            return "" + prefix + value;
        // format and escape everything else
        var formatter = get_formatter(name, raw_spec, format, formatters);
        return "" + prefix + string_1.escape(formatter(value, format, special_vars));
    });
    return str;
}
exports.replace_placeholders = replace_placeholders;
