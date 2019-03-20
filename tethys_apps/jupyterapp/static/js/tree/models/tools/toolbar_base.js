"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var logging_1 = require("core/logging");
var dom_1 = require("core/dom");
var build_views_1 = require("core/build_views");
var p = require("core/properties");
var dom_view_1 = require("core/dom_view");
var types_1 = require("core/util/types");
var model_1 = require("model");
var ToolbarBaseView = /** @class */ (function (_super) {
    tslib_1.__extends(ToolbarBaseView, _super);
    function ToolbarBaseView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ToolbarBaseView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this._tool_button_views = {};
        this._build_tool_button_views();
    };
    ToolbarBaseView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.properties.tools.change, function () { return _this._build_tool_button_views(); });
    };
    ToolbarBaseView.prototype.remove = function () {
        build_views_1.remove_views(this._tool_button_views);
        _super.prototype.remove.call(this);
    };
    ToolbarBaseView.prototype._build_tool_button_views = function () {
        var tools = (this.model._proxied_tools != null ? this.model._proxied_tools : this.model.tools); // XXX
        build_views_1.build_views(this._tool_button_views, tools, { parent: this }, function (tool) { return tool.button_view; });
    };
    ToolbarBaseView.prototype.render = function () {
        var _this = this;
        dom_1.empty(this.el);
        this.el.classList.add("bk-toolbar");
        this.el.classList.add("bk-toolbar-" + this.model.toolbar_location);
        if (this.model.logo != null) {
            var cls = this.model.logo === "grey" ? "bk-grey" : null;
            var logo = dom_1.a({ href: "https://bokeh.pydata.org/", target: "_blank", class: ["bk-logo", "bk-logo-small", cls] });
            this.el.appendChild(logo);
        }
        var bars = [];
        var el = function (tool) {
            return _this._tool_button_views[tool.id].el;
        };
        var gestures = this.model.gestures;
        for (var et in gestures) {
            bars.push(gestures[et].tools.map(el));
        }
        bars.push(this.model.actions.map(el));
        bars.push(this.model.inspectors.filter(function (tool) { return tool.toggleable; }).map(el));
        bars.push(this.model.help.map(el));
        for (var _i = 0, bars_1 = bars; _i < bars_1.length; _i++) {
            var bar = bars_1[_i];
            if (bar.length !== 0) {
                var el_1 = dom_1.div({ class: 'bk-button-bar' }, bar);
                this.el.appendChild(el_1);
            }
        }
    };
    return ToolbarBaseView;
}(dom_view_1.DOMView));
exports.ToolbarBaseView = ToolbarBaseView;
var ToolbarBase = /** @class */ (function (_super) {
    tslib_1.__extends(ToolbarBase, _super);
    function ToolbarBase(attrs) {
        return _super.call(this, attrs) || this;
    }
    ToolbarBase.initClass = function () {
        this.prototype.type = 'ToolbarBase';
        this.prototype.default_view = ToolbarBaseView;
        this.define({
            tools: [p.Array, []],
            logo: [p.String, 'normal'],
        });
        this.internal({
            gestures: [p.Any, function () { return ({
                    pan: { tools: [], active: null },
                    scroll: { tools: [], active: null },
                    pinch: { tools: [], active: null },
                    tap: { tools: [], active: null },
                    doubletap: { tools: [], active: null },
                    press: { tools: [], active: null },
                    rotate: { tools: [], active: null },
                    move: { tools: [], active: null },
                    multi: { tools: [], active: null },
                }); }],
            actions: [p.Array, []],
            inspectors: [p.Array, []],
            help: [p.Array, []],
            toolbar_location: [p.Location, 'right'],
        });
    };
    Object.defineProperty(ToolbarBase.prototype, "horizontal", {
        get: function () {
            return this.toolbar_location === "above" || this.toolbar_location === "below";
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ToolbarBase.prototype, "vertical", {
        get: function () {
            return this.toolbar_location === "left" || this.toolbar_location === "right";
        },
        enumerable: true,
        configurable: true
    });
    ToolbarBase.prototype._active_change = function (tool) {
        var event_type = tool.event_type;
        if (event_type == null)
            return;
        var event_types = types_1.isString(event_type) ? [event_type] : event_type;
        for (var _i = 0, event_types_1 = event_types; _i < event_types_1.length; _i++) {
            var et = event_types_1[_i];
            if (tool.active) {
                var currently_active_tool = this.gestures[et].active;
                if (currently_active_tool != null && tool != currently_active_tool) {
                    logging_1.logger.debug("Toolbar: deactivating tool: " + currently_active_tool.type + " (" + currently_active_tool.id + ") for event type '" + et + "'");
                    currently_active_tool.active = false;
                }
                this.gestures[et].active = tool;
                logging_1.logger.debug("Toolbar: activating tool: " + tool.type + " (" + tool.id + ") for event type '" + et + "'");
            }
            else
                this.gestures[et].active = null;
        }
    };
    return ToolbarBase;
}(model_1.Model));
exports.ToolbarBase = ToolbarBase;
ToolbarBase.initClass();
