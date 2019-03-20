"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("core/util/types");
var ImagePool = /** @class */ (function () {
    function ImagePool() {
        this.images = [];
    }
    ImagePool.prototype.pop = function () {
        var img = this.images.pop();
        return img != null ? img : new Image();
    };
    ImagePool.prototype.push = function (img) {
        var _a;
        if (this.images.length > 50)
            return;
        if (types_1.isArray(img))
            (_a = this.images).push.apply(_a, img);
        else
            this.images.push(img);
    };
    return ImagePool;
}());
exports.ImagePool = ImagePool;
