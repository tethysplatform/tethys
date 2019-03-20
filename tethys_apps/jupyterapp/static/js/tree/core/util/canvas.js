"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var SVGRenderingContext2D = require("canvas2svg");
exports.SVGRenderingContext2D = SVGRenderingContext2D;
function fixup_line_dash(ctx) {
    if (!ctx.setLineDash) {
        ctx.setLineDash = function (dash) {
            ctx.mozDash = dash;
            ctx.webkitLineDash = dash;
        };
    }
    if (!ctx.getLineDash) {
        ctx.getLineDash = function () {
            return ctx.mozDash;
        };
    }
}
function fixup_line_dash_offset(ctx) {
    ctx.setLineDashOffset = function (offset) {
        ctx.lineDashOffset = offset;
        ctx.mozDashOffset = offset;
        ctx.webkitLineDashOffset = offset;
    };
    ctx.getLineDashOffset = function () {
        return ctx.mozDashOffset;
    };
}
function fixup_image_smoothing(ctx) {
    ctx.setImageSmoothingEnabled = function (value) {
        ctx.imageSmoothingEnabled = value;
        ctx.mozImageSmoothingEnabled = value;
        ctx.oImageSmoothingEnabled = value;
        ctx.webkitImageSmoothingEnabled = value;
        ctx.msImageSmoothingEnabled = value;
    };
    ctx.getImageSmoothingEnabled = function () {
        var val = ctx.imageSmoothingEnabled;
        return val != null ? val : true;
    };
}
function fixup_measure_text(ctx) {
    if (ctx.measureText && ctx.html5MeasureText == null) {
        ctx.html5MeasureText = ctx.measureText;
        ctx.measureText = function (text) {
            var textMetrics = ctx.html5MeasureText(text);
            // fake it til you make it
            textMetrics.ascent = ctx.html5MeasureText("m").width * 1.6;
            return textMetrics;
        };
    }
}
function fixup_ellipse(ctx) {
    // implementing the ctx.ellipse function with bezier curves
    // we don't implement the startAngle, endAngle and anticlockwise arguments.
    function ellipse_bezier(x, y, radiusX, radiusY, rotation, _startAngle, _endAngle, anticlockwise) {
        if (anticlockwise === void 0) { anticlockwise = false; }
        var c = 0.551784; // see http://www.tinaja.com/glib/ellipse4.pdf
        ctx.translate(x, y);
        ctx.rotate(rotation);
        var rx = radiusX;
        var ry = radiusY;
        if (anticlockwise) {
            rx = -radiusX;
            ry = -radiusY;
        }
        ctx.moveTo(-rx, 0); // start point of first curve
        ctx.bezierCurveTo(-rx, ry * c, -rx * c, ry, 0, ry);
        ctx.bezierCurveTo(rx * c, ry, rx, ry * c, rx, 0);
        ctx.bezierCurveTo(rx, -ry * c, rx * c, -ry, 0, -ry);
        ctx.bezierCurveTo(-rx * c, -ry, -rx, -ry * c, -rx, 0);
        ctx.rotate(-rotation);
        ctx.translate(-x, -y);
    }
    if (!ctx.ellipse)
        ctx.ellipse = ellipse_bezier;
}
function fixup_ctx(ctx) {
    fixup_line_dash(ctx);
    fixup_line_dash_offset(ctx);
    fixup_image_smoothing(ctx);
    fixup_measure_text(ctx);
    fixup_ellipse(ctx);
}
exports.fixup_ctx = fixup_ctx;
function get_scale_ratio(ctx, hidpi, backend) {
    if (backend == "svg")
        return 1;
    else if (hidpi) {
        var devicePixelRatio_1 = window.devicePixelRatio || 1;
        var backingStoreRatio = ctx.webkitBackingStorePixelRatio ||
            ctx.mozBackingStorePixelRatio ||
            ctx.msBackingStorePixelRatio ||
            ctx.oBackingStorePixelRatio ||
            ctx.backingStorePixelRatio || 1;
        return devicePixelRatio_1 / backingStoreRatio;
    }
    else
        return 1;
}
exports.get_scale_ratio = get_scale_ratio;
