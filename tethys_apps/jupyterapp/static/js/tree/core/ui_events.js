"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var Hammer = require("hammerjs");
var signaling_1 = require("./signaling");
var logging_1 = require("./logging");
var dom_1 = require("./dom");
var wheel_1 = require("./util/wheel");
var array_1 = require("./util/array");
var object_1 = require("./util/object");
var types_1 = require("./util/types");
var bokeh_events_1 = require("./bokeh_events");
exports.is_mobile = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
var UIEvents = /** @class */ (function () {
    function UIEvents(plot_view, toolbar, hit_area, plot) {
        var _this = this;
        this.plot_view = plot_view;
        this.toolbar = toolbar;
        this.hit_area = hit_area;
        this.plot = plot;
        this.pan_start = new signaling_1.Signal(this, 'pan:start');
        this.pan = new signaling_1.Signal(this, 'pan');
        this.pan_end = new signaling_1.Signal(this, 'pan:end');
        this.pinch_start = new signaling_1.Signal(this, 'pinch:start');
        this.pinch = new signaling_1.Signal(this, 'pinch');
        this.pinch_end = new signaling_1.Signal(this, 'pinch:end');
        this.rotate_start = new signaling_1.Signal(this, 'rotate:start');
        this.rotate = new signaling_1.Signal(this, 'rotate');
        this.rotate_end = new signaling_1.Signal(this, 'rotate:end');
        this.tap = new signaling_1.Signal(this, 'tap');
        this.doubletap = new signaling_1.Signal(this, 'doubletap');
        this.press = new signaling_1.Signal(this, 'press');
        this.move_enter = new signaling_1.Signal(this, 'move:enter');
        this.move = new signaling_1.Signal(this, 'move');
        this.move_exit = new signaling_1.Signal(this, 'move:exit');
        this.scroll = new signaling_1.Signal(this, 'scroll');
        this.keydown = new signaling_1.Signal(this, 'keydown');
        this.keyup = new signaling_1.Signal(this, 'keyup');
        this.hammer = new Hammer(this.hit_area);
        this._configure_hammerjs();
        // Mouse & keyboard events not handled through hammerjs
        // We can 'add and forget' these event listeners because this.hit_area is a DOM element
        // that will be thrown away when the view is removed
        this.hit_area.addEventListener("mousemove", function (e) { return _this._mouse_move(e); });
        this.hit_area.addEventListener("mouseenter", function (e) { return _this._mouse_enter(e); });
        this.hit_area.addEventListener("mouseleave", function (e) { return _this._mouse_exit(e); });
        this.hit_area.addEventListener("wheel", function (e) { return _this._mouse_wheel(e); });
        // But we MUST remove listeners registered on document or we'll leak memory: register
        // 'this' as the listener (it implements the event listener interface, i.e. handleEvent)
        // instead of an anonymous function so we can easily refer back to it for removing
        document.addEventListener("keydown", this);
        document.addEventListener("keyup", this);
    }
    UIEvents.prototype.destroy = function () {
        this.hammer.destroy();
        document.removeEventListener("keydown", this);
        document.removeEventListener("keyup", this);
    };
    UIEvents.prototype.handleEvent = function (e) {
        if (e.type == "keydown")
            this._key_down(e);
        else if (e.type == "keyup")
            this._key_up(e);
    };
    UIEvents.prototype._configure_hammerjs = function () {
        var _this = this;
        // This is to be able to distinguish double taps from single taps
        this.hammer.get('doubletap').recognizeWith('tap');
        this.hammer.get('tap').requireFailure('doubletap');
        this.hammer.get('doubletap').dropRequireFailure('tap');
        this.hammer.on('doubletap', function (e) { return _this._doubletap(e); });
        this.hammer.on('tap', function (e) { return _this._tap(e); });
        this.hammer.on('press', function (e) { return _this._press(e); });
        this.hammer.get('pan').set({ direction: Hammer.DIRECTION_ALL });
        this.hammer.on('panstart', function (e) { return _this._pan_start(e); });
        this.hammer.on('pan', function (e) { return _this._pan(e); });
        this.hammer.on('panend', function (e) { return _this._pan_end(e); });
        this.hammer.get('pinch').set({ enable: true });
        this.hammer.on('pinchstart', function (e) { return _this._pinch_start(e); });
        this.hammer.on('pinch', function (e) { return _this._pinch(e); });
        this.hammer.on('pinchend', function (e) { return _this._pinch_end(e); });
        this.hammer.get('rotate').set({ enable: true });
        this.hammer.on('rotatestart', function (e) { return _this._rotate_start(e); });
        this.hammer.on('rotate', function (e) { return _this._rotate(e); });
        this.hammer.on('rotateend', function (e) { return _this._rotate_end(e); });
    };
    UIEvents.prototype.register_tool = function (tool_view) {
        var _this = this;
        var et = tool_view.model.event_type;
        if (et != null) {
            if (types_1.isString(et))
                this._register_tool(tool_view, et);
            else {
                // Multi-tools should only registered shared events once
                et.forEach(function (e, index) { return _this._register_tool(tool_view, e, index < 1); });
            }
        }
    };
    UIEvents.prototype._register_tool = function (tool_view, et, shared) {
        if (shared === void 0) { shared = true; }
        var v = tool_view;
        var id = v.model.id;
        var conditionally = function (fn) { return function (arg) {
            if (arg.id == id)
                fn(arg.e);
        }; };
        var unconditionally = function (fn) { return function (arg) {
            fn(arg.e);
        }; };
        switch (et) {
            case "pan": {
                if (v._pan_start != null)
                    v.connect(this.pan_start, conditionally(v._pan_start.bind(v)));
                if (v._pan != null)
                    v.connect(this.pan, conditionally(v._pan.bind(v)));
                if (v._pan_end != null)
                    v.connect(this.pan_end, conditionally(v._pan_end.bind(v)));
                break;
            }
            case "pinch": {
                if (v._pinch_start != null)
                    v.connect(this.pinch_start, conditionally(v._pinch_start.bind(v)));
                if (v._pinch != null)
                    v.connect(this.pinch, conditionally(v._pinch.bind(v)));
                if (v._pinch_end != null)
                    v.connect(this.pinch_end, conditionally(v._pinch_end.bind(v)));
                break;
            }
            case "rotate": {
                if (v._rotate_start != null)
                    v.connect(this.rotate_start, conditionally(v._rotate_start.bind(v)));
                if (v._rotate != null)
                    v.connect(this.rotate, conditionally(v._rotate.bind(v)));
                if (v._rotate_end != null)
                    v.connect(this.rotate_end, conditionally(v._rotate_end.bind(v)));
                break;
            }
            case "move": {
                if (v._move_enter != null)
                    v.connect(this.move_enter, conditionally(v._move_enter.bind(v)));
                if (v._move != null)
                    v.connect(this.move, conditionally(v._move.bind(v)));
                if (v._move_exit != null)
                    v.connect(this.move_exit, conditionally(v._move_exit.bind(v)));
                break;
            }
            case "tap": {
                if (v._tap != null)
                    v.connect(this.tap, conditionally(v._tap.bind(v)));
                break;
            }
            case "press": {
                if (v._press != null)
                    v.connect(this.press, conditionally(v._press.bind(v)));
                break;
            }
            case "scroll": {
                if (v._scroll != null)
                    v.connect(this.scroll, conditionally(v._scroll.bind(v)));
                break;
            }
            default:
                throw new Error("unsupported event_type: " + et);
        }
        // Skip shared events if registering multi-tool
        if (!shared)
            return;
        if (v._doubletap != null)
            v.connect(this.doubletap, unconditionally(v._doubletap.bind(v)));
        if (v._keydown != null)
            v.connect(this.keydown, unconditionally(v._keydown.bind(v)));
        if (v._keyup != null)
            v.connect(this.keyup, unconditionally(v._keyup.bind(v)));
        // Dual touch hack part 1/2
        // This is a hack for laptops with touch screen who may be pinching or scrolling
        // in order to use the wheel zoom tool. If it's a touch screen the WheelZoomTool event
        // will be linked to pinch. But we also want to trigger in the case of a scroll.
        if (exports.is_mobile && v._scroll != null && et == 'pinch') {
            logging_1.logger.debug("Registering scroll on touch screen");
            v.connect(this.scroll, conditionally(v._scroll.bind(v)));
        }
    };
    UIEvents.prototype._hit_test_renderers = function (sx, sy) {
        var views = this.plot_view.get_renderer_views();
        for (var _i = 0, _a = array_1.reversed(views); _i < _a.length; _i++) {
            var view = _a[_i];
            var level = view.model.level;
            if ((level == 'annotation' || level == 'overlay') && view.interactive_hit != null) {
                if (view.interactive_hit(sx, sy))
                    return view;
            }
        }
        return null;
    };
    UIEvents.prototype._hit_test_frame = function (sx, sy) {
        return this.plot_view.frame.bbox.contains(sx, sy);
    };
    UIEvents.prototype._trigger = function (signal, e, srcEvent) {
        var _this = this;
        var gestures = this.toolbar.gestures;
        var event_type = signal.name;
        var base_type = event_type.split(":")[0];
        var view = this._hit_test_renderers(e.sx, e.sy);
        switch (base_type) {
            case "move": {
                var active_gesture = gestures[base_type].active;
                if (active_gesture != null)
                    this.trigger(signal, e, active_gesture.id);
                var active_inspectors = this.toolbar.inspectors.filter(function (t) { return t.active; });
                var cursor = "default";
                // the event happened on a renderer
                if (view != null) {
                    cursor = view.cursor(e.sx, e.sy) || cursor;
                    if (!object_1.isEmpty(active_inspectors)) {
                        // override event_type to cause inspectors to clear overlays
                        signal = this.move_exit;
                        event_type = signal.name;
                    }
                    // the event happened on the plot frame but off a renderer
                }
                else if (this._hit_test_frame(e.sx, e.sy)) {
                    if (!object_1.isEmpty(active_inspectors)) {
                        cursor = "crosshair";
                    }
                }
                this.plot_view.set_cursor(cursor);
                active_inspectors.map(function (inspector) { return _this.trigger(signal, e, inspector.id); });
                break;
            }
            case "tap": {
                var target = srcEvent.target;
                if (target != null && target != this.hit_area)
                    return; // don't trigger bokeh events
                if (view != null && view.on_hit != null)
                    view.on_hit(e.sx, e.sy);
                var active_gesture = gestures[base_type].active;
                if (active_gesture != null)
                    this.trigger(signal, e, active_gesture.id);
                break;
            }
            case "scroll": {
                // Dual touch hack part 2/2
                // This is a hack for laptops with touch screen who may be pinching or scrolling
                // in order to use the wheel zoom tool. If it's a touch screen the WheelZoomTool event
                // will be linked to pinch. But we also want to trigger in the case of a scroll.
                var base = exports.is_mobile ? "pinch" : "scroll";
                var active_gesture = gestures[base].active;
                if (active_gesture != null) {
                    srcEvent.preventDefault();
                    srcEvent.stopPropagation();
                    this.trigger(signal, e, active_gesture.id);
                }
                break;
            }
            default: {
                var active_gesture = gestures[base_type].active;
                if (active_gesture != null)
                    this.trigger(signal, e, active_gesture.id);
            }
        }
        this._trigger_bokeh_event(e);
    };
    UIEvents.prototype.trigger = function (signal, e, id) {
        if (id === void 0) { id = null; }
        signal.emit({ id: id, e: e });
    };
    UIEvents.prototype._trigger_bokeh_event = function (e) {
        var event_cls = bokeh_events_1.BokehEvent.event_class(e);
        if (event_cls != null)
            this.plot.trigger_event(event_cls.from_event(e));
        else
            logging_1.logger.debug("Unhandled event of type " + e.type);
    };
    UIEvents.prototype._get_sxy = function (event) {
        // XXX: jsdom doesn't support TouchEvent constructor
        function is_touch(event) {
            return typeof TouchEvent !== "undefined" && event instanceof TouchEvent;
        }
        var _a = is_touch(event) ? (event.touches.length != 0 ? event.touches : event.changedTouches)[0] : event, pageX = _a.pageX, pageY = _a.pageY;
        var _b = dom_1.offset(this.hit_area), left = _b.left, top = _b.top;
        return {
            sx: pageX - left,
            sy: pageY - top,
        };
    };
    UIEvents.prototype._gesture_event = function (e) {
        return tslib_1.__assign({ type: e.type }, this._get_sxy(e.srcEvent), { deltaX: e.deltaX, deltaY: e.deltaY, scale: e.scale, shiftKey: e.srcEvent.shiftKey });
    };
    UIEvents.prototype._tap_event = function (e) {
        return tslib_1.__assign({ type: e.type }, this._get_sxy(e.srcEvent), { shiftKey: e.srcEvent.shiftKey });
    };
    UIEvents.prototype._move_event = function (e) {
        return tslib_1.__assign({ type: e.type }, this._get_sxy(e));
    };
    UIEvents.prototype._scroll_event = function (e) {
        return tslib_1.__assign({ type: e.type }, this._get_sxy(e), { delta: wheel_1.getDeltaY(e) });
    };
    UIEvents.prototype._key_event = function (e) {
        return { type: e.type, keyCode: e.keyCode };
    };
    UIEvents.prototype._pan_start = function (e) {
        var ev = this._gesture_event(e);
        // back out delta to get original center point
        ev.sx -= e.deltaX;
        ev.sy -= e.deltaY;
        this._trigger(this.pan_start, ev, e.srcEvent);
    };
    UIEvents.prototype._pan = function (e) {
        this._trigger(this.pan, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._pan_end = function (e) {
        this._trigger(this.pan_end, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._pinch_start = function (e) {
        this._trigger(this.pinch_start, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._pinch = function (e) {
        this._trigger(this.pinch, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._pinch_end = function (e) {
        this._trigger(this.pinch_end, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._rotate_start = function (e) {
        this._trigger(this.rotate_start, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._rotate = function (e) {
        this._trigger(this.rotate, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._rotate_end = function (e) {
        this._trigger(this.rotate_end, this._gesture_event(e), e.srcEvent);
    };
    UIEvents.prototype._tap = function (e) {
        this._trigger(this.tap, this._tap_event(e), e.srcEvent);
    };
    UIEvents.prototype._doubletap = function (e) {
        // NOTE: doubletap event triggered unconditionally
        var ev = this._tap_event(e);
        this._trigger_bokeh_event(ev);
        this.trigger(this.doubletap, ev);
    };
    UIEvents.prototype._press = function (e) {
        this._trigger(this.press, this._tap_event(e), e.srcEvent);
    };
    UIEvents.prototype._mouse_enter = function (e) {
        this._trigger(this.move_enter, this._move_event(e), e);
    };
    UIEvents.prototype._mouse_move = function (e) {
        this._trigger(this.move, this._move_event(e), e);
    };
    UIEvents.prototype._mouse_exit = function (e) {
        this._trigger(this.move_exit, this._move_event(e), e);
    };
    UIEvents.prototype._mouse_wheel = function (e) {
        this._trigger(this.scroll, this._scroll_event(e), e);
    };
    UIEvents.prototype._key_down = function (e) {
        // NOTE: keyup event triggered unconditionally
        this.trigger(this.keydown, this._key_event(e));
    };
    UIEvents.prototype._key_up = function (e) {
        // NOTE: keyup event triggered unconditionally
        this.trigger(this.keyup, this._key_event(e));
    };
    return UIEvents;
}());
exports.UIEvents = UIEvents;
