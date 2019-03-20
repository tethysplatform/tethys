"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var signaling_1 = require("./signaling");
var enums = require("./enums");
var svg_colors_1 = require("./util/svg_colors");
var color_1 = require("./util/color");
var array_1 = require("./util/array");
var arrayable_1 = require("./util/arrayable");
var types_1 = require("./util/types");
signaling_1.Signal; // XXX: silence TS, because `Signal` appears in declarations due to Signalable
function valueToString(value) {
    try {
        return JSON.stringify(value);
    }
    catch (_a) {
        return value.toString();
    }
}
function isSpec(obj) {
    return types_1.isPlainObject(obj) &&
        ((obj.value === undefined ? 0 : 1) +
            (obj.field === undefined ? 0 : 1) +
            (obj.expr === undefined ? 0 : 1) == 1); // garbage JS XOR
}
exports.isSpec = isSpec;
//
// Property base class
//
var Property = /** @class */ (function (_super) {
    tslib_1.__extends(Property, _super);
    function Property(obj, attr, default_value) {
        var _this = _super.call(this) || this;
        _this.obj = obj;
        _this.attr = attr;
        _this.default_value = default_value;
        _this.optional = false;
        _this.obj = obj;
        _this.attr = attr;
        _this.default_value = default_value;
        _this.change = new signaling_1.Signal0(_this.obj, "change");
        _this._init();
        _this.connect(_this.change, function () { return _this._init(); });
        return _this;
    }
    Property.prototype.update = function () {
        this._init();
    };
    // ----- customizable policies
    Property.prototype.init = function () { };
    Property.prototype.transform = function (values) {
        return values;
    };
    Property.prototype.validate = function (_value) { };
    // ----- property accessors
    Property.prototype.value = function (do_spec_transform) {
        if (do_spec_transform === void 0) { do_spec_transform = true; }
        if (this.spec.value === undefined)
            throw new Error("attempted to retrieve property value for property without value specification");
        var ret = this.transform([this.spec.value])[0];
        if (this.spec.transform != null && do_spec_transform)
            ret = this.spec.transform.compute(ret);
        return ret;
    };
    Property.prototype.array = function (source) {
        if (!this.dataspec)
            throw new Error("attempted to retrieve property array for non-dataspec property");
        var ret;
        if (this.spec.field != null) {
            ret = this.transform(source.get_column(this.spec.field));
            if (ret == null)
                throw new Error("attempted to retrieve property array for nonexistent field '" + this.spec.field + "'");
        }
        else if (this.spec.expr != null) {
            ret = this.transform(this.spec.expr.v_compute(source));
        }
        else {
            var length_1 = source.get_length();
            if (length_1 == null)
                length_1 = 1;
            var value = this.value(false); // don't apply any spec transform
            ret = array_1.repeat(value, length_1);
        }
        if (this.spec.transform != null)
            ret = this.spec.transform.v_compute(ret);
        return ret;
    };
    // ----- private methods
    /*protected*/ Property.prototype._init = function () {
        var _a;
        var obj = this.obj;
        var attr = this.attr;
        var attr_value = obj.getv(attr);
        if (attr_value === undefined) {
            var default_value = this.default_value;
            if (default_value !== undefined)
                attr_value = default_value(obj);
            else
                attr_value = null;
            obj.setv((_a = {}, _a[attr] = attr_value, _a), { silent: true, defaults: true });
        }
        if (types_1.isArray(attr_value))
            this.spec = { value: attr_value };
        else if (isSpec(attr_value))
            this.spec = attr_value;
        else
            this.spec = { value: attr_value };
        if (this.spec.field != null && !types_1.isString(this.spec.field))
            throw new Error("field value for property '" + attr + "' is not a string");
        if (this.spec.value != null)
            this.validate(this.spec.value);
        this.init();
    };
    Property.prototype.toString = function () {
        /*${this.name}*/
        return "Prop(" + this.obj + "." + this.attr + ", spec: " + valueToString(this.spec) + ")";
    };
    return Property;
}(signaling_1.Signalable()));
exports.Property = Property;
Property.prototype.dataspec = false;
//
// Simple Properties
//
function simple_prop(name, pred) {
    return /** @class */ (function (_super) {
        tslib_1.__extends(class_1, _super);
        function class_1() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        class_1.prototype.validate = function (value) {
            if (!pred(value))
                throw new Error(name + " property '" + this.attr + "' given invalid value: " + valueToString(value));
        };
        return class_1;
    }(Property));
}
exports.simple_prop = simple_prop;
var Any = /** @class */ (function (_super) {
    tslib_1.__extends(Any, _super);
    function Any() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Any;
}(simple_prop("Any", function (_x) { return true; })));
exports.Any = Any;
var Array = /** @class */ (function (_super) {
    tslib_1.__extends(Array, _super);
    function Array() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Array;
}(simple_prop("Array", function (x) { return types_1.isArray(x) || x instanceof Float64Array; })));
exports.Array = Array;
var Bool = /** @class */ (function (_super) {
    tslib_1.__extends(Bool, _super);
    function Bool() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Bool;
}(simple_prop("Bool", types_1.isBoolean)));
exports.Bool = Bool;
exports.Boolean = Bool;
var Color = /** @class */ (function (_super) {
    tslib_1.__extends(Color, _super);
    function Color() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Color;
}(simple_prop("Color", function (x) { return svg_colors_1.is_svg_color(x.toLowerCase()) || x.substring(0, 1) == "#" || color_1.valid_rgb(x); })));
exports.Color = Color;
var Instance = /** @class */ (function (_super) {
    tslib_1.__extends(Instance, _super);
    function Instance() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Instance;
}(simple_prop("Instance", function (x) { return x.properties != null; })));
exports.Instance = Instance;
// TODO (bev) separate booleans?
var Number = /** @class */ (function (_super) {
    tslib_1.__extends(Number, _super);
    function Number() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Number;
}(simple_prop("Number", function (x) { return types_1.isNumber(x) || types_1.isBoolean(x); })));
exports.Number = Number;
exports.Int = Number;
// TODO extend Number instead of copying it's predicate
//class Percent extends Number("Percent", (x) -> 0 <= x <= 1.0)
var Percent = /** @class */ (function (_super) {
    tslib_1.__extends(Percent, _super);
    function Percent() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Percent;
}(simple_prop("Number", function (x) { return (types_1.isNumber(x) || types_1.isBoolean(x)) && 0 <= x && x <= 1.0; })));
exports.Percent = Percent;
var String = /** @class */ (function (_super) {
    tslib_1.__extends(String, _super);
    function String() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return String;
}(simple_prop("String", types_1.isString)));
exports.String = String;
// TODO (bev) don't think this exists python side
var Font = /** @class */ (function (_super) {
    tslib_1.__extends(Font, _super);
    function Font() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Font;
}(String));
exports.Font = Font;
//
// Enum properties
//
function enum_prop(name, enum_values) {
    return /** @class */ (function (_super) {
        tslib_1.__extends(class_2, _super);
        function class_2() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        return class_2;
    }(simple_prop(name, function (x) { return array_1.includes(enum_values, x); })));
}
exports.enum_prop = enum_prop;
var Anchor = /** @class */ (function (_super) {
    tslib_1.__extends(Anchor, _super);
    function Anchor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Anchor;
}(enum_prop("Anchor", enums.LegendLocation)));
exports.Anchor = Anchor;
var AngleUnits = /** @class */ (function (_super) {
    tslib_1.__extends(AngleUnits, _super);
    function AngleUnits() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return AngleUnits;
}(enum_prop("AngleUnits", enums.AngleUnits)));
exports.AngleUnits = AngleUnits;
var Direction = /** @class */ (function (_super) {
    tslib_1.__extends(Direction, _super);
    function Direction() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Direction.prototype.transform = function (values) {
        var result = new Uint8Array(values.length);
        for (var i = 0; i < values.length; i++) {
            switch (values[i]) {
                case "clock":
                    result[i] = 0;
                    break;
                case "anticlock":
                    result[i] = 1;
                    break;
            }
        }
        return result;
    };
    return Direction;
}(enum_prop("Direction", enums.Direction)));
exports.Direction = Direction;
var Dimension = /** @class */ (function (_super) {
    tslib_1.__extends(Dimension, _super);
    function Dimension() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Dimension;
}(enum_prop("Dimension", enums.Dimension)));
exports.Dimension = Dimension;
var Dimensions = /** @class */ (function (_super) {
    tslib_1.__extends(Dimensions, _super);
    function Dimensions() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Dimensions;
}(enum_prop("Dimensions", enums.Dimensions)));
exports.Dimensions = Dimensions;
var FontStyle = /** @class */ (function (_super) {
    tslib_1.__extends(FontStyle, _super);
    function FontStyle() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return FontStyle;
}(enum_prop("FontStyle", enums.FontStyle)));
exports.FontStyle = FontStyle;
var LatLon = /** @class */ (function (_super) {
    tslib_1.__extends(LatLon, _super);
    function LatLon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LatLon;
}(enum_prop("LatLon", enums.LatLon)));
exports.LatLon = LatLon;
var LineCap = /** @class */ (function (_super) {
    tslib_1.__extends(LineCap, _super);
    function LineCap() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LineCap;
}(enum_prop("LineCap", enums.LineCap)));
exports.LineCap = LineCap;
var LineJoin = /** @class */ (function (_super) {
    tslib_1.__extends(LineJoin, _super);
    function LineJoin() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LineJoin;
}(enum_prop("LineJoin", enums.LineJoin)));
exports.LineJoin = LineJoin;
var LegendLocation = /** @class */ (function (_super) {
    tslib_1.__extends(LegendLocation, _super);
    function LegendLocation() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LegendLocation;
}(enum_prop("LegendLocation", enums.LegendLocation)));
exports.LegendLocation = LegendLocation;
var Location = /** @class */ (function (_super) {
    tslib_1.__extends(Location, _super);
    function Location() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Location;
}(enum_prop("Location", enums.Location)));
exports.Location = Location;
var OutputBackend = /** @class */ (function (_super) {
    tslib_1.__extends(OutputBackend, _super);
    function OutputBackend() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return OutputBackend;
}(enum_prop("OutputBackend", enums.OutputBackend)));
exports.OutputBackend = OutputBackend;
var Orientation = /** @class */ (function (_super) {
    tslib_1.__extends(Orientation, _super);
    function Orientation() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Orientation;
}(enum_prop("Orientation", enums.Orientation)));
exports.Orientation = Orientation;
var VerticalAlign = /** @class */ (function (_super) {
    tslib_1.__extends(VerticalAlign, _super);
    function VerticalAlign() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return VerticalAlign;
}(enum_prop("VerticalAlign", enums.VerticalAlign)));
exports.VerticalAlign = VerticalAlign;
var TextAlign = /** @class */ (function (_super) {
    tslib_1.__extends(TextAlign, _super);
    function TextAlign() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return TextAlign;
}(enum_prop("TextAlign", enums.TextAlign)));
exports.TextAlign = TextAlign;
var TextBaseline = /** @class */ (function (_super) {
    tslib_1.__extends(TextBaseline, _super);
    function TextBaseline() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return TextBaseline;
}(enum_prop("TextBaseline", enums.TextBaseline)));
exports.TextBaseline = TextBaseline;
var RenderLevel = /** @class */ (function (_super) {
    tslib_1.__extends(RenderLevel, _super);
    function RenderLevel() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return RenderLevel;
}(enum_prop("RenderLevel", enums.RenderLevel)));
exports.RenderLevel = RenderLevel;
var RenderMode = /** @class */ (function (_super) {
    tslib_1.__extends(RenderMode, _super);
    function RenderMode() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return RenderMode;
}(enum_prop("RenderMode", enums.RenderMode)));
exports.RenderMode = RenderMode;
var SizingMode = /** @class */ (function (_super) {
    tslib_1.__extends(SizingMode, _super);
    function SizingMode() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return SizingMode;
}(enum_prop("SizingMode", enums.SizingMode)));
exports.SizingMode = SizingMode;
var SpatialUnits = /** @class */ (function (_super) {
    tslib_1.__extends(SpatialUnits, _super);
    function SpatialUnits() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return SpatialUnits;
}(enum_prop("SpatialUnits", enums.SpatialUnits)));
exports.SpatialUnits = SpatialUnits;
var Distribution = /** @class */ (function (_super) {
    tslib_1.__extends(Distribution, _super);
    function Distribution() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Distribution;
}(enum_prop("Distribution", enums.Distribution)));
exports.Distribution = Distribution;
var StepMode = /** @class */ (function (_super) {
    tslib_1.__extends(StepMode, _super);
    function StepMode() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return StepMode;
}(enum_prop("StepMode", enums.StepMode)));
exports.StepMode = StepMode;
var PaddingUnits = /** @class */ (function (_super) {
    tslib_1.__extends(PaddingUnits, _super);
    function PaddingUnits() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return PaddingUnits;
}(enum_prop("PaddingUnits", enums.PaddingUnits)));
exports.PaddingUnits = PaddingUnits;
var StartEnd = /** @class */ (function (_super) {
    tslib_1.__extends(StartEnd, _super);
    function StartEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return StartEnd;
}(enum_prop("StartEnd", enums.StartEnd)));
exports.StartEnd = StartEnd;
//
// Units Properties
//
function units_prop(name, valid_units, default_units) {
    return /** @class */ (function (_super) {
        tslib_1.__extends(class_3, _super);
        function class_3() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        class_3.prototype.init = function () {
            if (this.spec.units == null)
                this.spec.units = default_units;
            var units = this.spec.units;
            if (!array_1.includes(valid_units, units))
                throw new Error(name + " units must be one of " + valid_units + ", given invalid value: " + units);
        };
        Object.defineProperty(class_3.prototype, "units", {
            get: function () {
                return this.spec.units;
            },
            set: function (units) {
                this.spec.units = units;
            },
            enumerable: true,
            configurable: true
        });
        return class_3;
    }(Number));
}
exports.units_prop = units_prop;
var Angle = /** @class */ (function (_super) {
    tslib_1.__extends(Angle, _super);
    function Angle() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Angle.prototype.transform = function (values) {
        if (this.spec.units == "deg")
            values = arrayable_1.map(values, function (x) { return x * Math.PI / 180.0; });
        values = arrayable_1.map(values, function (x) { return -x; });
        return _super.prototype.transform.call(this, values);
    };
    return Angle;
}(units_prop("Angle", enums.AngleUnits, "rad")));
exports.Angle = Angle;
var Distance = /** @class */ (function (_super) {
    tslib_1.__extends(Distance, _super);
    function Distance() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Distance;
}(units_prop("Distance", enums.SpatialUnits, "data")));
exports.Distance = Distance;
//
// DataSpec properties
//
var AngleSpec = /** @class */ (function (_super) {
    tslib_1.__extends(AngleSpec, _super);
    function AngleSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return AngleSpec;
}(Angle));
exports.AngleSpec = AngleSpec;
AngleSpec.prototype.dataspec = true;
var ColorSpec = /** @class */ (function (_super) {
    tslib_1.__extends(ColorSpec, _super);
    function ColorSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return ColorSpec;
}(Color));
exports.ColorSpec = ColorSpec;
ColorSpec.prototype.dataspec = true;
var DistanceSpec = /** @class */ (function (_super) {
    tslib_1.__extends(DistanceSpec, _super);
    function DistanceSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return DistanceSpec;
}(Distance));
exports.DistanceSpec = DistanceSpec;
DistanceSpec.prototype.dataspec = true;
var FontSizeSpec = /** @class */ (function (_super) {
    tslib_1.__extends(FontSizeSpec, _super);
    function FontSizeSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return FontSizeSpec;
}(String));
exports.FontSizeSpec = FontSizeSpec;
FontSizeSpec.prototype.dataspec = true;
var MarkerSpec = /** @class */ (function (_super) {
    tslib_1.__extends(MarkerSpec, _super);
    function MarkerSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return MarkerSpec;
}(String));
exports.MarkerSpec = MarkerSpec;
MarkerSpec.prototype.dataspec = true;
var NumberSpec = /** @class */ (function (_super) {
    tslib_1.__extends(NumberSpec, _super);
    function NumberSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return NumberSpec;
}(Number));
exports.NumberSpec = NumberSpec;
NumberSpec.prototype.dataspec = true;
var StringSpec = /** @class */ (function (_super) {
    tslib_1.__extends(StringSpec, _super);
    function StringSpec() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return StringSpec;
}(String));
exports.StringSpec = StringSpec;
StringSpec.prototype.dataspec = true;
