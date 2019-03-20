"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var min = Math.min, max = Math.max;
function empty() {
    return {
        minX: Infinity,
        minY: Infinity,
        maxX: -Infinity,
        maxY: -Infinity,
    };
}
exports.empty = empty;
function positive_x() {
    return {
        minX: Number.MIN_VALUE,
        minY: -Infinity,
        maxX: Infinity,
        maxY: Infinity,
    };
}
exports.positive_x = positive_x;
function positive_y() {
    return {
        minX: -Infinity,
        minY: Number.MIN_VALUE,
        maxX: Infinity,
        maxY: Infinity,
    };
}
exports.positive_y = positive_y;
function union(a, b) {
    return {
        minX: min(a.minX, b.minX),
        maxX: max(a.maxX, b.maxX),
        minY: min(a.minY, b.minY),
        maxY: max(a.maxY, b.maxY),
    };
}
exports.union = union;
var BBox = /** @class */ (function () {
    function BBox(box) {
        if ('x0' in box && 'y0' in box && 'x1' in box && 'y1' in box) {
            var _a = box, x0 = _a.x0, y0 = _a.y0, x1 = _a.x1, y1 = _a.y1;
            if (!(x0 <= x1 && y0 <= y1))
                throw new Error("invalid bbox {x0: " + x0 + ", y0: " + y0 + ", x1: " + x1 + ", y1: " + y1 + "}");
            this.x0 = x0;
            this.y0 = y0;
            this.x1 = x1;
            this.y1 = y1;
        }
        else {
            var _b = box, x = _b.x, y = _b.y, width = _b.width, height = _b.height;
            if (!(width >= 0 && height >= 0))
                throw new Error("invalid bbox {x: " + x + ", y: " + y + ", width: " + width + ", height: " + height + "}");
            this.x0 = x;
            this.y0 = y;
            this.x1 = x + width;
            this.y1 = y + height;
        }
    }
    Object.defineProperty(BBox.prototype, "minX", {
        get: function () { return this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "minY", {
        get: function () { return this.y0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "maxX", {
        get: function () { return this.x1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "maxY", {
        get: function () { return this.y1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "left", {
        get: function () { return this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "top", {
        get: function () { return this.y0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "right", {
        get: function () { return this.x1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "bottom", {
        get: function () { return this.y1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "p0", {
        get: function () { return [this.x0, this.y0]; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "p1", {
        get: function () { return [this.x1, this.y1]; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "x", {
        get: function () { return this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "y", {
        get: function () { return this.y0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "width", {
        get: function () { return this.x1 - this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "height", {
        get: function () { return this.y1 - this.y0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "rect", {
        get: function () { return { x: this.x, y: this.y, width: this.width, height: this.height }; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "h_range", {
        get: function () { return { start: this.x0, end: this.x1 }; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "v_range", {
        get: function () { return { start: this.y0, end: this.y1 }; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "ranges", {
        get: function () { return [this.h_range, this.v_range]; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "aspect", {
        get: function () { return this.width / this.height; },
        enumerable: true,
        configurable: true
    });
    BBox.prototype.contains = function (x, y) {
        return x >= this.x0 && x <= this.x1 && y >= this.y0 && y <= this.y1;
    };
    BBox.prototype.clip = function (x, y) {
        if (x < this.x0)
            x = this.x0;
        else if (x > this.x1)
            x = this.x1;
        if (y < this.y0)
            y = this.y0;
        else if (y > this.y1)
            y = this.y1;
        return [x, y];
    };
    BBox.prototype.union = function (that) {
        return new BBox({
            x0: min(this.x0, that.x0),
            y0: min(this.y0, that.y0),
            x1: max(this.x1, that.x1),
            y1: max(this.y1, that.y1),
        });
    };
    return BBox;
}());
exports.BBox = BBox;
