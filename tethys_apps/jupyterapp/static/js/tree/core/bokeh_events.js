"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var logging_1 = require("./logging");
var object_1 = require("./util/object");
var event_classes = {};
function register_event_class(event_name) {
    return function (event_cls) {
        event_cls.prototype.event_name = event_name;
        event_classes[event_name] = event_cls;
    };
}
exports.register_event_class = register_event_class;
function register_with_event(event_cls) {
    var models = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        models[_i - 1] = arguments[_i];
    }
    var applicable_models = event_cls.prototype.applicable_models.concat(models);
    event_cls.prototype.applicable_models = applicable_models;
}
exports.register_with_event = register_with_event;
var BokehEvent = /** @class */ (function () {
    function BokehEvent(options) {
        if (options === void 0) { options = {}; }
        this.model_id = null;
        this._options = options;
        if (options.model_id) {
            this.model_id = options.model_id;
        }
    }
    BokehEvent.prototype.set_model_id = function (id) {
        this._options.model_id = id;
        this.model_id = id;
        return this;
    };
    BokehEvent.prototype.is_applicable_to = function (obj) {
        return this.applicable_models.some(function (model) { return obj instanceof model; });
    };
    BokehEvent.event_class = function (e) {
        // Given an event with a type attribute matching the event_name,
        // return the appropriate BokehEvent class
        if (e.type) {
            return event_classes[e.type];
        }
        else {
            logging_1.logger.warn('BokehEvent.event_class required events with a string type attribute');
        }
    };
    BokehEvent.prototype.toJSON = function () {
        return {
            event_name: this.event_name,
            event_values: object_1.clone(this._options),
        };
    };
    BokehEvent.prototype._customize_event = function (_model) {
        return this;
    };
    return BokehEvent;
}());
exports.BokehEvent = BokehEvent;
BokehEvent.prototype.applicable_models = [];
var ButtonClick = /** @class */ (function (_super) {
    tslib_1.__extends(ButtonClick, _super);
    function ButtonClick() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ButtonClick = tslib_1.__decorate([
        register_event_class("button_click")
    ], ButtonClick);
    return ButtonClick;
}(BokehEvent));
exports.ButtonClick = ButtonClick;
// A UIEvent is an event originating on a PlotCanvas this includes
// DOM events such as keystrokes as well as hammer events and LOD events.
var UIEvent = /** @class */ (function (_super) {
    tslib_1.__extends(UIEvent, _super);
    function UIEvent() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return UIEvent;
}(BokehEvent));
exports.UIEvent = UIEvent;
var LODStart = /** @class */ (function (_super) {
    tslib_1.__extends(LODStart, _super);
    function LODStart() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LODStart = tslib_1.__decorate([
        register_event_class("lodstart")
    ], LODStart);
    return LODStart;
}(UIEvent));
exports.LODStart = LODStart;
var LODEnd = /** @class */ (function (_super) {
    tslib_1.__extends(LODEnd, _super);
    function LODEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LODEnd = tslib_1.__decorate([
        register_event_class("lodend")
    ], LODEnd);
    return LODEnd;
}(UIEvent));
exports.LODEnd = LODEnd;
var SelectionGeometry = /** @class */ (function (_super) {
    tslib_1.__extends(SelectionGeometry, _super);
    function SelectionGeometry(options) {
        var _this = _super.call(this, options) || this;
        _this.geometry = options.geometry;
        _this.final = options.final;
        return _this;
    }
    SelectionGeometry = tslib_1.__decorate([
        register_event_class("selectiongeometry")
    ], SelectionGeometry);
    return SelectionGeometry;
}(UIEvent));
exports.SelectionGeometry = SelectionGeometry;
var Reset = /** @class */ (function (_super) {
    tslib_1.__extends(Reset, _super);
    function Reset() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Reset = tslib_1.__decorate([
        register_event_class("reset")
    ], Reset);
    return Reset;
}(UIEvent));
exports.Reset = Reset;
var PointEvent = /** @class */ (function (_super) {
    tslib_1.__extends(PointEvent, _super);
    function PointEvent(options) {
        var _this = _super.call(this, options) || this;
        _this.sx = options.sx;
        _this.sy = options.sy;
        _this.x = null;
        _this.y = null;
        return _this;
    }
    PointEvent.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({ sx: e.sx, sy: e.sy, model_id: model_id });
    };
    PointEvent.prototype._customize_event = function (plot) {
        var xscale = plot.plot_canvas.frame.xscales['default'];
        var yscale = plot.plot_canvas.frame.yscales['default'];
        this.x = xscale.invert(this.sx);
        this.y = yscale.invert(this.sy);
        this._options['x'] = this.x;
        this._options['y'] = this.y;
        return this;
    };
    return PointEvent;
}(UIEvent));
exports.PointEvent = PointEvent;
var Pan = /** @class */ (function (_super) {
    tslib_1.__extends(Pan, _super);
    function Pan(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this.delta_x = options.delta_x;
        _this.delta_y = options.delta_y;
        return _this;
    }
    Pan.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({
            sx: e.sx,
            sy: e.sy,
            delta_x: e.deltaX,
            delta_y: e.deltaY,
            direction: e.direction,
            model_id: model_id,
        });
    };
    Pan = tslib_1.__decorate([
        register_event_class("pan")
    ], Pan);
    return Pan;
}(PointEvent));
exports.Pan = Pan;
var Pinch = /** @class */ (function (_super) {
    tslib_1.__extends(Pinch, _super);
    function Pinch(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this.scale = options.scale;
        return _this;
    }
    Pinch.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({
            sx: e.sx,
            sy: e.sy,
            scale: e.scale,
            model_id: model_id,
        });
    };
    Pinch = tslib_1.__decorate([
        register_event_class("pinch")
    ], Pinch);
    return Pinch;
}(PointEvent));
exports.Pinch = Pinch;
var MouseWheel = /** @class */ (function (_super) {
    tslib_1.__extends(MouseWheel, _super);
    function MouseWheel(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this.delta = options.delta;
        return _this;
    }
    MouseWheel.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({
            sx: e.sx,
            sy: e.sy,
            delta: e.delta,
            model_id: model_id,
        });
    };
    MouseWheel = tslib_1.__decorate([
        register_event_class("wheel")
    ], MouseWheel);
    return MouseWheel;
}(PointEvent));
exports.MouseWheel = MouseWheel;
var MouseMove = /** @class */ (function (_super) {
    tslib_1.__extends(MouseMove, _super);
    function MouseMove() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MouseMove = tslib_1.__decorate([
        register_event_class("mousemove")
    ], MouseMove);
    return MouseMove;
}(PointEvent));
exports.MouseMove = MouseMove;
var MouseEnter = /** @class */ (function (_super) {
    tslib_1.__extends(MouseEnter, _super);
    function MouseEnter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MouseEnter = tslib_1.__decorate([
        register_event_class("mouseenter")
    ], MouseEnter);
    return MouseEnter;
}(PointEvent));
exports.MouseEnter = MouseEnter;
var MouseLeave = /** @class */ (function (_super) {
    tslib_1.__extends(MouseLeave, _super);
    function MouseLeave() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MouseLeave = tslib_1.__decorate([
        register_event_class("mouseleave")
    ], MouseLeave);
    return MouseLeave;
}(PointEvent));
exports.MouseLeave = MouseLeave;
var Tap = /** @class */ (function (_super) {
    tslib_1.__extends(Tap, _super);
    function Tap() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Tap = tslib_1.__decorate([
        register_event_class("tap")
    ], Tap);
    return Tap;
}(PointEvent));
exports.Tap = Tap;
var DoubleTap = /** @class */ (function (_super) {
    tslib_1.__extends(DoubleTap, _super);
    function DoubleTap() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DoubleTap = tslib_1.__decorate([
        register_event_class("doubletap")
    ], DoubleTap);
    return DoubleTap;
}(PointEvent));
exports.DoubleTap = DoubleTap;
var Press = /** @class */ (function (_super) {
    tslib_1.__extends(Press, _super);
    function Press() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Press = tslib_1.__decorate([
        register_event_class("press")
    ], Press);
    return Press;
}(PointEvent));
exports.Press = Press;
var PanStart = /** @class */ (function (_super) {
    tslib_1.__extends(PanStart, _super);
    function PanStart() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PanStart = tslib_1.__decorate([
        register_event_class("panstart")
    ], PanStart);
    return PanStart;
}(PointEvent));
exports.PanStart = PanStart;
var PanEnd = /** @class */ (function (_super) {
    tslib_1.__extends(PanEnd, _super);
    function PanEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PanEnd = tslib_1.__decorate([
        register_event_class("panend")
    ], PanEnd);
    return PanEnd;
}(PointEvent));
exports.PanEnd = PanEnd;
var PinchStart = /** @class */ (function (_super) {
    tslib_1.__extends(PinchStart, _super);
    function PinchStart() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PinchStart = tslib_1.__decorate([
        register_event_class("pinchstart")
    ], PinchStart);
    return PinchStart;
}(PointEvent));
exports.PinchStart = PinchStart;
var PinchEnd = /** @class */ (function (_super) {
    tslib_1.__extends(PinchEnd, _super);
    function PinchEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PinchEnd = tslib_1.__decorate([
        register_event_class("pinchend")
    ], PinchEnd);
    return PinchEnd;
}(PointEvent));
exports.PinchEnd = PinchEnd;
