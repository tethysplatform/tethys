"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var dom_1 = require("core/dom");
var logging_1 = require("core/logging");
var types_1 = require("core/util/types");
var array_1 = require("core/util/array");
var action_tool_1 = require("./actions/action_tool");
var help_tool_1 = require("./actions/help_tool");
var gesture_tool_1 = require("./gestures/gesture_tool");
var inspect_tool_1 = require("./inspectors/inspect_tool");
var toolbar_base_1 = require("./toolbar_base");
var tool_proxy_1 = require("./tool_proxy");
var layout_dom_1 = require("../layouts/layout_dom");
var build_views_1 = require("core/build_views");
var ProxyToolbar = /** @class */ (function (_super) {
    tslib_1.__extends(ProxyToolbar, _super);
    function ProxyToolbar(attrs) {
        return _super.call(this, attrs) || this;
    }
    ProxyToolbar.initClass = function () {
        this.prototype.type = "ProxyToolbar";
    };
    ProxyToolbar.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._init_tools();
        this._merge_tools();
    };
    ProxyToolbar.prototype._init_tools = function () {
        var _loop_1 = function (tool) {
            if (tool instanceof inspect_tool_1.InspectTool) {
                if (!array_1.any(this_1.inspectors, function (t) { return t.id == tool.id; }))
                    this_1.inspectors = this_1.inspectors.concat([tool]);
            }
            else if (tool instanceof help_tool_1.HelpTool) {
                if (!array_1.any(this_1.help, function (t) { return t.id == tool.id; }))
                    this_1.help = this_1.help.concat([tool]);
            }
            else if (tool instanceof action_tool_1.ActionTool) {
                if (!array_1.any(this_1.actions, function (t) { return t.id == tool.id; }))
                    this_1.actions = this_1.actions.concat([tool]);
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
                }
            }
        };
        var this_1 = this;
        for (var _i = 0, _a = this.tools; _i < _a.length; _i++) {
            var tool = _a[_i];
            _loop_1(tool);
        }
    };
    ProxyToolbar.prototype._merge_tools = function () {
        var _this = this;
        var _a;
        // Go through all the tools on the toolbar and replace them with
        // a proxy e.g. PanTool, BoxSelectTool, etc.
        this._proxied_tools = [];
        var inspectors = {};
        var actions = {};
        var gestures = {};
        var new_help_tools = [];
        var new_help_urls = [];
        for (var _i = 0, _b = this.help; _i < _b.length; _i++) {
            var helptool = _b[_i];
            if (!array_1.includes(new_help_urls, helptool.redirect)) {
                new_help_tools.push(helptool);
                new_help_urls.push(helptool.redirect);
            }
        }
        (_a = this._proxied_tools).push.apply(_a, new_help_tools);
        this.help = new_help_tools;
        for (var event_type in this.gestures) {
            var gesture = this.gestures[event_type];
            if (!(event_type in gestures)) {
                gestures[event_type] = {};
            }
            for (var _c = 0, _d = gesture.tools; _c < _d.length; _c++) {
                var tool = _d[_c];
                if (!(tool.type in gestures[event_type])) {
                    gestures[event_type][tool.type] = [];
                }
                gestures[event_type][tool.type].push(tool);
            }
        }
        for (var _e = 0, _f = this.inspectors; _e < _f.length; _e++) {
            var tool = _f[_e];
            if (!(tool.type in inspectors)) {
                inspectors[tool.type] = [];
            }
            inspectors[tool.type].push(tool);
        }
        for (var _g = 0, _h = this.actions; _g < _h.length; _g++) {
            var tool = _h[_g];
            if (!(tool.type in actions)) {
                actions[tool.type] = [];
            }
            actions[tool.type].push(tool);
        }
        // Add a proxy for each of the groups of tools.
        var make_proxy = function (tools, active) {
            if (active === void 0) { active = false; }
            var proxy = new tool_proxy_1.ToolProxy({ tools: tools, active: active });
            _this._proxied_tools.push(proxy);
            return proxy;
        };
        for (var event_type in gestures) {
            var gesture = this.gestures[event_type];
            gesture.tools = [];
            for (var tool_type in gestures[event_type]) {
                var tools = gestures[event_type][tool_type];
                if (tools.length > 0) {
                    var proxy = make_proxy(tools);
                    gesture.tools.push(proxy);
                    this.connect(proxy.properties.active.change, this._active_change.bind(this, proxy));
                }
            }
        }
        this.actions = [];
        for (var tool_type in actions) {
            var tools = actions[tool_type];
            if (tools.length > 0)
                this.actions.push(make_proxy(tools)); // XXX
        }
        this.inspectors = [];
        for (var tool_type in inspectors) {
            var tools = inspectors[tool_type];
            if (tools.length > 0)
                this.inspectors.push(make_proxy(tools, true)); // XXX
        }
        for (var et in this.gestures) {
            var gesture = this.gestures[et];
            if (gesture.tools.length == 0)
                continue;
            gesture.tools = array_1.sortBy(gesture.tools, function (tool) { return tool.default_order; });
            if (!(et == 'pinch' || et == 'scroll' || et == 'multi'))
                gesture.tools[0].active = true;
        }
    };
    return ProxyToolbar;
}(toolbar_base_1.ToolbarBase));
exports.ProxyToolbar = ProxyToolbar;
ProxyToolbar.initClass();
var ToolbarBoxView = /** @class */ (function (_super) {
    tslib_1.__extends(ToolbarBoxView, _super);
    function ToolbarBoxView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ToolbarBoxView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.model.toolbar.toolbar_location = this.model.toolbar_location;
        this._toolbar_views = {};
        build_views_1.build_views(this._toolbar_views, [this.model.toolbar], { parent: this });
    };
    ToolbarBoxView.prototype.remove = function () {
        build_views_1.remove_views(this._toolbar_views);
        _super.prototype.remove.call(this);
    };
    ToolbarBoxView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-toolbar-box");
    };
    ToolbarBoxView.prototype.render = function () {
        _super.prototype.render.call(this);
        var toolbar = this._toolbar_views[this.model.toolbar.id];
        toolbar.render();
        dom_1.empty(this.el);
        this.el.appendChild(toolbar.el);
    };
    ToolbarBoxView.prototype.get_width = function () {
        return this.model.toolbar.vertical ? 30 : null;
    };
    ToolbarBoxView.prototype.get_height = function () {
        return this.model.toolbar.horizontal ? 30 : null;
    };
    return ToolbarBoxView;
}(layout_dom_1.LayoutDOMView));
exports.ToolbarBoxView = ToolbarBoxView;
var ToolbarBox = /** @class */ (function (_super) {
    tslib_1.__extends(ToolbarBox, _super);
    function ToolbarBox(attrs) {
        return _super.call(this, attrs) || this;
    }
    ToolbarBox.initClass = function () {
        this.prototype.type = 'ToolbarBox';
        this.prototype.default_view = ToolbarBoxView;
        this.define({
            toolbar: [p.Instance],
            toolbar_location: [p.Location, "right"],
        });
    };
    Object.defineProperty(ToolbarBox.prototype, "sizing_mode", {
        // XXX: we are overriding LayoutDOM.sizing_mode here. That's a bad
        // hack, but currently every layoutable is allowed to have its
        // sizing mode configured, which is wrong. Another example of this
        // is PlotCanvas which only works with strech_both sizing mode.
        get: function () {
            switch (this.toolbar_location) {
                case "above":
                case "below": {
                    return "scale_width";
                }
                case "left":
                case "right": {
                    return "scale_height";
                }
            }
        },
        enumerable: true,
        configurable: true
    });
    return ToolbarBox;
}(layout_dom_1.LayoutDOM));
exports.ToolbarBox = ToolbarBox;
ToolbarBox.initClass();
