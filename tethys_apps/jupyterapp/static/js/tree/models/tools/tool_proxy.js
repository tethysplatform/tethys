"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var signaling_1 = require("core/signaling");
var model_1 = require("../../model");
var ToolProxy = /** @class */ (function (_super) {
    tslib_1.__extends(ToolProxy, _super);
    function ToolProxy(attrs) {
        return _super.call(this, attrs) || this;
    }
    ToolProxy.initClass = function () {
        this.prototype.type = "ToolProxy";
        this.define({
            tools: [p.Array, []],
            active: [p.Bool, false],
            disabled: [p.Bool, false],
        });
    };
    Object.defineProperty(ToolProxy.prototype, "button_view", {
        // Operates all the tools given only one button
        get: function () {
            return this.tools[0].button_view;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ToolProxy.prototype, "event_type", {
        get: function () {
            return this.tools[0].event_type;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ToolProxy.prototype, "tooltip", {
        get: function () {
            return this.tools[0].tooltip;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ToolProxy.prototype, "tool_name", {
        get: function () {
            return this.tools[0].tool_name;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ToolProxy.prototype, "icon", {
        get: function () {
            return this.tools[0].computed_icon;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ToolProxy.prototype, "computed_icon", {
        get: function () {
            return this.icon;
        },
        enumerable: true,
        configurable: true
    });
    ToolProxy.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.do = new signaling_1.Signal0(this, "do");
    };
    ToolProxy.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.do, function () { return _this.doit(); });
        this.connect(this.properties.active.change, function () { return _this.set_active(); });
    };
    ToolProxy.prototype.doit = function () {
        for (var _i = 0, _a = this.tools; _i < _a.length; _i++) {
            var tool = _a[_i];
            tool.do.emit();
        }
    };
    ToolProxy.prototype.set_active = function () {
        for (var _i = 0, _a = this.tools; _i < _a.length; _i++) {
            var tool = _a[_i];
            tool.active = this.active;
        }
    };
    return ToolProxy;
}(model_1.Model));
exports.ToolProxy = ToolProxy;
ToolProxy.initClass();
