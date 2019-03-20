"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var p = require("core/properties");
var types_1 = require("core/util/types");
var Range = /** @class */ (function (_super) {
    tslib_1.__extends(Range, _super);
    function Range(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.have_updated_interactively = false;
        return _this;
    }
    Range.initClass = function () {
        this.prototype.type = "Range";
        this.define({
            callback: [p.Any],
            bounds: [p.Any],
            min_interval: [p.Any],
            max_interval: [p.Any],
        });
        this.internal({
            plots: [p.Array, []],
        });
    };
    Range.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.change, function () { return _this._emit_callback(); });
    };
    Range.prototype.reset = function () {
        /**
         * This method should be reimplemented by subclasses and ensure that
         * the callback, if exists, is executed at completion.
         */
        this.change.emit();
    };
    Range.prototype._emit_callback = function () {
        if (this.callback != null) {
            if (types_1.isFunction(this.callback))
                this.callback(this);
            else
                this.callback.execute(this, {});
        }
    };
    Object.defineProperty(Range.prototype, "is_reversed", {
        get: function () {
            return this.start > this.end;
        },
        enumerable: true,
        configurable: true
    });
    return Range;
}(model_1.Model));
exports.Range = Range;
Range.initClass();
