"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var annotation_1 = require("./annotation");
var visuals_1 = require("core/visuals");
var p = require("core/properties");
var ArrowHead = /** @class */ (function (_super) {
    tslib_1.__extends(ArrowHead, _super);
    function ArrowHead(attrs) {
        return _super.call(this, attrs) || this;
    }
    ArrowHead.initClass = function () {
        this.prototype.type = 'ArrowHead';
        this.define({
            size: [p.Number, 25],
        });
    };
    ArrowHead.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.visuals = new visuals_1.Visuals(this);
    };
    return ArrowHead;
}(annotation_1.Annotation));
exports.ArrowHead = ArrowHead;
ArrowHead.initClass();
var OpenHead = /** @class */ (function (_super) {
    tslib_1.__extends(OpenHead, _super);
    function OpenHead(attrs) {
        return _super.call(this, attrs) || this;
    }
    OpenHead.initClass = function () {
        this.prototype.type = 'OpenHead';
        this.mixins(['line']);
    };
    OpenHead.prototype.clip = function (ctx, i) {
        // This method should not begin or close a path
        this.visuals.line.set_vectorize(ctx, i);
        ctx.moveTo(0.5 * this.size, this.size);
        ctx.lineTo(0.5 * this.size, -2);
        ctx.lineTo(-0.5 * this.size, -2);
        ctx.lineTo(-0.5 * this.size, this.size);
        ctx.lineTo(0, 0);
        ctx.lineTo(0.5 * this.size, this.size);
    };
    OpenHead.prototype.render = function (ctx, i) {
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            ctx.beginPath();
            ctx.moveTo(0.5 * this.size, this.size);
            ctx.lineTo(0, 0);
            ctx.lineTo(-0.5 * this.size, this.size);
            ctx.stroke();
        }
    };
    return OpenHead;
}(ArrowHead));
exports.OpenHead = OpenHead;
OpenHead.initClass();
var NormalHead = /** @class */ (function (_super) {
    tslib_1.__extends(NormalHead, _super);
    function NormalHead(attrs) {
        return _super.call(this, attrs) || this;
    }
    NormalHead.initClass = function () {
        this.prototype.type = 'NormalHead';
        this.mixins(['line', 'fill']);
        this.override({
            fill_color: 'black',
        });
    };
    NormalHead.prototype.clip = function (ctx, i) {
        // This method should not begin or close a path
        this.visuals.line.set_vectorize(ctx, i);
        ctx.moveTo(0.5 * this.size, this.size);
        ctx.lineTo(0.5 * this.size, -2);
        ctx.lineTo(-0.5 * this.size, -2);
        ctx.lineTo(-0.5 * this.size, this.size);
        ctx.lineTo(0.5 * this.size, this.size);
    };
    NormalHead.prototype.render = function (ctx, i) {
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_vectorize(ctx, i);
            this._normal(ctx, i);
            ctx.fill();
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            this._normal(ctx, i);
            ctx.stroke();
        }
    };
    NormalHead.prototype._normal = function (ctx, _i) {
        ctx.beginPath();
        ctx.moveTo(0.5 * this.size, this.size);
        ctx.lineTo(0, 0);
        ctx.lineTo(-0.5 * this.size, this.size);
        ctx.closePath();
    };
    return NormalHead;
}(ArrowHead));
exports.NormalHead = NormalHead;
NormalHead.initClass();
var VeeHead = /** @class */ (function (_super) {
    tslib_1.__extends(VeeHead, _super);
    function VeeHead(attrs) {
        return _super.call(this, attrs) || this;
    }
    VeeHead.initClass = function () {
        this.prototype.type = 'VeeHead';
        this.mixins(['line', 'fill']);
        this.override({
            fill_color: 'black',
        });
    };
    VeeHead.prototype.clip = function (ctx, i) {
        // This method should not begin or close a path
        this.visuals.line.set_vectorize(ctx, i);
        ctx.moveTo(0.5 * this.size, this.size);
        ctx.lineTo(0.5 * this.size, -2);
        ctx.lineTo(-0.5 * this.size, -2);
        ctx.lineTo(-0.5 * this.size, this.size);
        ctx.lineTo(0, 0.5 * this.size);
        ctx.lineTo(0.5 * this.size, this.size);
    };
    VeeHead.prototype.render = function (ctx, i) {
        if (this.visuals.fill.doit) {
            this.visuals.fill.set_vectorize(ctx, i);
            this._vee(ctx, i);
            ctx.fill();
        }
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            this._vee(ctx, i);
            ctx.stroke();
        }
    };
    VeeHead.prototype._vee = function (ctx, _i) {
        ctx.beginPath();
        ctx.moveTo(0.5 * this.size, this.size);
        ctx.lineTo(0, 0);
        ctx.lineTo(-0.5 * this.size, this.size);
        ctx.lineTo(0, 0.5 * this.size);
        ctx.closePath();
    };
    return VeeHead;
}(ArrowHead));
exports.VeeHead = VeeHead;
VeeHead.initClass();
var TeeHead = /** @class */ (function (_super) {
    tslib_1.__extends(TeeHead, _super);
    function TeeHead(attrs) {
        return _super.call(this, attrs) || this;
    }
    TeeHead.initClass = function () {
        this.prototype.type = 'TeeHead';
        this.mixins(['line']);
    };
    TeeHead.prototype.render = function (ctx, i) {
        if (this.visuals.line.doit) {
            this.visuals.line.set_vectorize(ctx, i);
            ctx.beginPath();
            ctx.moveTo(0.5 * this.size, 0);
            ctx.lineTo(-0.5 * this.size, 0);
            ctx.stroke();
        }
    };
    TeeHead.prototype.clip = function (_ctx, _i) { };
    return TeeHead;
}(ArrowHead));
exports.TeeHead = TeeHead;
TeeHead.initClass();
