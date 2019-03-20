"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var Numbro = require("numbro");
var compile_template = require("underscore.template");
var tz = require("timezone");
var p = require("core/properties");
var dom_1 = require("core/dom");
var types_1 = require("core/util/types");
var model_1 = require("../../../model");
var CellFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(CellFormatter, _super);
    function CellFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    CellFormatter.prototype.doFormat = function (_row, _cell, value, _columnDef, _dataContext) {
        if (value == null)
            return "";
        else
            return (value + "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    };
    return CellFormatter;
}(model_1.Model));
exports.CellFormatter = CellFormatter;
var StringFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(StringFormatter, _super);
    function StringFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    StringFormatter.initClass = function () {
        this.prototype.type = 'StringFormatter';
        this.define({
            font_style: [p.FontStyle, "normal"],
            text_align: [p.TextAlign, "left"],
            text_color: [p.Color],
        });
    };
    StringFormatter.prototype.doFormat = function (_row, _cell, value, _columnDef, _dataContext) {
        var _a = this, font_style = _a.font_style, text_align = _a.text_align, text_color = _a.text_color;
        var text = dom_1.span({}, value == null ? "" : "" + value);
        switch (font_style) {
            case "bold":
                text.style.fontWeight = "bold";
                break;
            case "italic":
                text.style.fontStyle = "italic";
                break;
        }
        if (text_align != null)
            text.style.textAlign = text_align;
        if (text_color != null)
            text.style.color = text_color;
        return text.outerHTML;
    };
    return StringFormatter;
}(CellFormatter));
exports.StringFormatter = StringFormatter;
StringFormatter.initClass();
var NumberFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(NumberFormatter, _super);
    function NumberFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    NumberFormatter.initClass = function () {
        this.prototype.type = 'NumberFormatter';
        this.define({
            format: [p.String, '0,0'],
            language: [p.String, 'en'],
            rounding: [p.String, 'round'],
        });
    };
    NumberFormatter.prototype.doFormat = function (row, cell, value, columnDef, dataContext) {
        var _this = this;
        var _a = this, format = _a.format, language = _a.language;
        var rounding = (function () {
            switch (_this.rounding) {
                case "round":
                case "nearest": return Math.round;
                case "floor":
                case "rounddown": return Math.floor;
                case "ceil":
                case "roundup": return Math.ceil;
            }
        })();
        value = Numbro.format(value, format, language, rounding);
        return _super.prototype.doFormat.call(this, row, cell, value, columnDef, dataContext);
    };
    return NumberFormatter;
}(StringFormatter));
exports.NumberFormatter = NumberFormatter;
NumberFormatter.initClass();
var BooleanFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(BooleanFormatter, _super);
    function BooleanFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    BooleanFormatter.initClass = function () {
        this.prototype.type = 'BooleanFormatter';
        this.define({
            icon: [p.String, 'check'],
        });
    };
    BooleanFormatter.prototype.doFormat = function (_row, _cell, value, _columnDef, _dataContext) {
        return !!value ? dom_1.i({ class: this.icon }).outerHTML : "";
    };
    return BooleanFormatter;
}(CellFormatter));
exports.BooleanFormatter = BooleanFormatter;
BooleanFormatter.initClass();
var DateFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(DateFormatter, _super);
    function DateFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    DateFormatter.initClass = function () {
        this.prototype.type = 'DateFormatter';
        this.define({
            format: [p.String, 'ISO-8601'],
        });
    };
    DateFormatter.prototype.getFormat = function () {
        // using definitions provided here: https://api.jqueryui.com/datepicker/
        // except not implementing TICKS
        switch (this.format) {
            case "ATOM":
            case "W3C":
            case "RFC-3339":
            case "ISO-8601":
                return "%Y-%m-%d";
            case "COOKIE":
                return "%a, %d %b %Y";
            case "RFC-850":
                return "%A, %d-%b-%y";
            case "RFC-1123":
            case "RFC-2822":
                return "%a, %e %b %Y";
            case "RSS":
            case "RFC-822":
            case "RFC-1036":
                return "%a, %e %b %y";
            case "TIMESTAMP":
                return undefined;
            default:
                return this.format;
        }
    };
    DateFormatter.prototype.doFormat = function (row, cell, value, columnDef, dataContext) {
        value = types_1.isString(value) ? parseInt(value, 10) : value;
        var date = tz(value, this.getFormat());
        return _super.prototype.doFormat.call(this, row, cell, date, columnDef, dataContext);
    };
    return DateFormatter;
}(CellFormatter));
exports.DateFormatter = DateFormatter;
DateFormatter.initClass();
var HTMLTemplateFormatter = /** @class */ (function (_super) {
    tslib_1.__extends(HTMLTemplateFormatter, _super);
    function HTMLTemplateFormatter(attrs) {
        return _super.call(this, attrs) || this;
    }
    HTMLTemplateFormatter.initClass = function () {
        this.prototype.type = 'HTMLTemplateFormatter';
        this.define({
            template: [p.String, '<%= value %>'],
        });
    };
    HTMLTemplateFormatter.prototype.doFormat = function (_row, _cell, value, _columnDef, dataContext) {
        var template = this.template;
        if (value == null)
            return "";
        else {
            var compiled_template = compile_template(template);
            var context = tslib_1.__assign({}, dataContext, { value: value });
            return compiled_template(context);
        }
    };
    return HTMLTemplateFormatter;
}(CellFormatter));
exports.HTMLTemplateFormatter = HTMLTemplateFormatter;
HTMLTemplateFormatter.initClass();
