"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var logging_1 = require("core/logging");
var types_1 = require("core/util/types");
var array_1 = require("core/util/array");
var action_tool_1 = require("./actions/action_tool");
var help_tool_1 = require("./actions/help_tool");
var gesture_tool_1 = require("./gestures/gesture_tool");
var inspect_tool_1 = require("./inspectors/inspect_tool");
var toolbar_base_1 = require("./toolbar_base");
var Toolbar = /** @class */ (function (_super) {
    tslib_1.__extends(Toolbar, _super);
    function Toolbar(attrs) {
        return _super.call(this, attrs) || this;
    }
    Toolbar.initClass = function () {
        this.prototype.type = 'Toolbar';
        this.prototype.default_view = toolbar_base_1.ToolbarBaseView;
        this.define({
            active_drag: [p.Any, 'auto'],
            active_inspect: [p.Any, 'auto'],
            active_scroll: [p.Any, 'auto'],
            active_tap: [p.Any, 'auto'],
            active_multi: [p.Any, null],
        });
    };
    Toolbar.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._init_tools();
    };
    Toolbar.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.properties.tools.change, function () { return _this._init_tools(); });
    };
    Toolbar.prototype._init_tools = function () {
        var _this = this;
        var _loop_1 = function (tool) {
            if (tool instanceof inspect_tool_1.InspectTool) {
                if (!array_1.any(this_1.inspectors, function (t) { return t.id == tool.id; })) {
                    this_1.inspectors = this_1.inspectors.concat([tool]);
                }
            }
            else if (tool instanceof help_tool_1.HelpTool) {
                if (!array_1.any(this_1.help, function (t) { return t.id == tool.id; })) {
                    this_1.help = this_1.help.concat([tool]);
                }
            }
            else if (tool instanceof action_tool_1.ActionTool) {
                if (!array_1.any(this_1.actions, function (t) { return t.id == tool.id; })) {
                    this_1.actions = this_1.actions.concat([tool]);
                }
            }
            else if (tool instanceof gesture_tool_1.GestureTool) {
                var event_types = void 0;
                var multi = void 0;
                if (types_1.isString(tool.event_type)) {
                    event_types = [tool.event_type];
                    multi = false;
                }
                else {
                    event_types = tool.event_type || [];
                    multi = true;
                }
                for (var _i = 0, event_types_1 = event_types; _i < event_types_1.length; _i++) {
                    var et = event_types_1[_i];
                    if (!(et in this_1.gestures)) {
                        logging_1.logger.warn("Toolbar: unknown event type '" + et + "' for tool: " + tool.type + " (" + tool.id + ")");
                        continue;
                    }
                    if (multi)
                        et = "multi";
                    if (!array_1.any(this_1.gestures[et].tools, function (t) { return t.id == tool.id; }))
                        this_1.gestures[et].tools = this_1.gestures[et].tools.concat([tool]);
                    this_1.connect(tool.properties.active.change, this_1._active_change.bind(this_1, tool));
                }
            }
        };
        var this_1 = this;
        for (var _i = 0, _a = this.tools; _i < _a.length; _i++) {
            var tool = _a[_i];
            _loop_1(tool);
        }
        if (this.active_inspect == 'auto') {
            // do nothing as all tools are active be default
        }
        else if (this.active_inspect instanceof inspect_tool_1.InspectTool) {
            for (var _b = 0, _c = this.inspectors; _b < _c.length; _b++) {
                var inspector = _c[_b];
                if (inspector != this.active_inspect)
                    inspector.active = false;
            }
        }
        else if (types_1.isArray(this.active_inspect)) {
            for (var _d = 0, _e = this.inspectors; _d < _e.length; _d++) {
                var inspector = _e[_d];
                if (!array_1.includes(this.active_inspect, inspector))
                    inspector.active = false;
            }
        }
        else if (this.active_inspect == null) {
            for (var _f = 0, _g = this.inspectors; _f < _g.length; _f++) {
                var inspector = _g[_f];
                inspector.active = false;
            }
        }
        var _activate_gesture = function (tool) {
            if (tool.active) {
                // tool was activated by a proxy, but we need to finish configuration manually
                _this._active_change(tool);
            }
            else
                tool.active = true;
        };
        for (var et in this.gestures) {
            var gesture = this.gestures[et];
            if (gesture.tools.length == 0)
                continue;
            gesture.tools = array_1.sortBy(gesture.tools, function (tool) { return tool.default_order; });
            if (et == 'tap') {
                if (this.active_tap == null)
                    continue;
                if (this.active_tap == 'auto')
                    _activate_gesture(gesture.tools[0]);
                else
                    _activate_gesture(this.active_tap);
            }
            if (et == 'pan') {
                if (this.active_drag == null)
                    continue;
                if (this.active_drag == 'auto')
                    _activate_gesture(gesture.tools[0]);
                else
                    _activate_gesture(this.active_drag);
            }
            if (et == 'pinch' || et == 'scroll') {
                if (this.active_scroll == null || this.active_scroll == 'auto')
                    continue;
                _activate_gesture(this.active_scroll);
            }
            if (this.active_multi != null)
                _activate_gesture(this.active_multi);
        }
    };
    return Toolbar;
}(toolbar_base_1.ToolbarBase));
exports.Toolbar = Toolbar;
Toolbar.initClass();
