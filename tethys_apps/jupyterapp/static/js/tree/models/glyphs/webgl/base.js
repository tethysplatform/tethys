"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var color_1 = require("core/util/color");
var logging_1 = require("core/logging");
var BaseGLGlyph = /** @class */ (function () {
    function BaseGLGlyph(gl, glyph) {
        this.gl = gl;
        this.glyph = glyph;
        this.nvertices = 0;
        this.size_changed = false;
        this.data_changed = false;
        this.visuals_changed = false;
        this.init();
    }
    BaseGLGlyph.prototype.set_data_changed = function (n) {
        if (n != this.nvertices) {
            this.nvertices = n;
            this.size_changed = true;
        }
        this.data_changed = true;
    };
    BaseGLGlyph.prototype.set_visuals_changed = function () {
        this.visuals_changed = true;
    };
    BaseGLGlyph.prototype.render = function (_ctx, indices, mainglyph) {
        var _a;
        // Get transform
        var _b = [0, 1, 2], a = _b[0], b = _b[1], c = _b[2];
        var wx = 1; // Weights to scale our vectors
        var wy = 1;
        var _c = this.glyph.renderer.map_to_screen([a * wx, b * wx, c * wx], [a * wy, b * wy, c * wy]), dx = _c[0], dy = _c[1];
        if (isNaN(dx[0] + dx[1] + dx[2] + dy[0] + dy[1] + dy[2])) {
            logging_1.logger.warn("WebGL backend (" + this.glyph.model.type + "): falling back to canvas rendering");
            return false;
        }
        // Try again, but with weighs so we're looking at ~100 in screen coordinates
        wx = 100 / Math.min(Math.max(Math.abs(dx[1] - dx[0]), 1e-12), 1e12);
        wy = 100 / Math.min(Math.max(Math.abs(dy[1] - dy[0]), 1e-12), 1e12);
        _a = this.glyph.renderer.map_to_screen([a * wx, b * wx, c * wx], [a * wy, b * wy, c * wy]), dx = _a[0], dy = _a[1];
        // Test how linear it is
        if ((Math.abs((dx[1] - dx[0]) - (dx[2] - dx[1])) > 1e-6) ||
            (Math.abs((dy[1] - dy[0]) - (dy[2] - dy[1])) > 1e-6)) {
            logging_1.logger.warn("WebGL backend (" + this.glyph.model.type + "): falling back to canvas rendering");
            return false;
        }
        var _d = [(dx[1] - dx[0]) / wx, (dy[1] - dy[0]) / wy], sx = _d[0], sy = _d[1];
        var _e = this.glyph.renderer.plot_view.gl.canvas, width = _e.width, height = _e.height;
        var trans = {
            pixel_ratio: this.glyph.renderer.plot_view.canvas.pixel_ratio,
            width: width, height: height,
            dx: dx[0] / sx, dy: dy[0] / sy, sx: sx, sy: sy,
        };
        this.draw(indices, mainglyph, trans);
        return true;
    };
    return BaseGLGlyph;
}());
exports.BaseGLGlyph = BaseGLGlyph;
function line_width(width) {
    // Increase small values to make it more similar to canvas
    if (width < 2) {
        width = Math.sqrt(width * 2);
    }
    return width;
}
exports.line_width = line_width;
function fill_array_with_float(n, val) {
    var a = new Float32Array(n);
    for (var i = 0, end = n; i < end; i++) {
        a[i] = val;
    }
    return a;
}
exports.fill_array_with_float = fill_array_with_float;
function fill_array_with_vec(n, m, val) {
    var a = new Float32Array(n * m);
    for (var i = 0; i < n; i++) {
        for (var j = 0; j < m; j++) {
            a[i * m + j] = val[j];
        }
    }
    return a;
}
exports.fill_array_with_vec = fill_array_with_vec;
function visual_prop_is_singular(visual, propname) {
    // This touches the internals of the visual, so we limit use in this function
    // See renderer.ts:cache_select() for similar code
    return visual[propname].spec.value !== undefined;
}
exports.visual_prop_is_singular = visual_prop_is_singular;
function attach_float(prog, vbo, att_name, n, visual, name) {
    // Attach a float attribute to the program. Use singleton value if we can,
    // otherwise use VBO to apply array.
    if (!visual.doit) {
        vbo.used = false;
        prog.set_attribute(att_name, 'float', [0]);
    }
    else if (visual_prop_is_singular(visual, name)) {
        vbo.used = false;
        prog.set_attribute(att_name, 'float', visual[name].value());
    }
    else {
        vbo.used = true;
        var a = new Float32Array(visual.cache[name + '_array']);
        vbo.set_size(n * 4);
        vbo.set_data(0, a);
        prog.set_attribute(att_name, 'float', vbo);
    }
}
exports.attach_float = attach_float;
function attach_color(prog, vbo, att_name, n, visual, prefix) {
    // Attach the color attribute to the program. If there's just one color,
    // then use this single color for all vertices (no VBO). Otherwise we
    // create an array and upload that to the VBO, which we attahce to the prog.
    var rgba;
    var m = 4;
    var colorname = prefix + '_color';
    var alphaname = prefix + '_alpha';
    if (!visual.doit) {
        // Don't draw (draw transparent)
        vbo.used = false;
        prog.set_attribute(att_name, 'vec4', [0, 0, 0, 0]);
    }
    else if (visual_prop_is_singular(visual, colorname) && visual_prop_is_singular(visual, alphaname)) {
        // Nice and simple; both color and alpha are singular
        vbo.used = false;
        rgba = color_1.color2rgba(visual[colorname].value(), visual[alphaname].value());
        prog.set_attribute(att_name, 'vec4', rgba);
    }
    else {
        // Use vbo; we need an array for both the color and the alpha
        var alphas = void 0, colors = void 0;
        vbo.used = true;
        // Get array of colors
        if (visual_prop_is_singular(visual, colorname)) {
            colors = ((function () {
                var result = [];
                for (var i = 0, end = n; i < end; i++) {
                    result.push(visual[colorname].value());
                }
                return result;
            })());
        }
        else {
            colors = visual.cache[colorname + '_array'];
        }
        // Get array of alphas
        if (visual_prop_is_singular(visual, alphaname)) {
            alphas = fill_array_with_float(n, visual[alphaname].value());
        }
        else {
            alphas = visual.cache[alphaname + '_array'];
        }
        // Create array of rgbs
        var a = new Float32Array(n * m);
        for (var i = 0, end = n; i < end; i++) {
            rgba = color_1.color2rgba(colors[i], alphas[i]);
            for (var j = 0, endj = m; j < endj; j++) {
                a[(i * m) + j] = rgba[j];
            }
        }
        // Attach vbo
        vbo.set_size(n * m * 4);
        vbo.set_data(0, a);
        prog.set_attribute(att_name, 'vec4', vbo);
    }
}
exports.attach_color = attach_color;
