"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gloo2_1 = require("gloo2");
var base_1 = require("./base");
var markers_vert_1 = require("./markers.vert");
var markers_frag_1 = require("./markers.frag");
var circle_1 = require("../circle");
var arrayable_1 = require("core/util/arrayable");
var logging_1 = require("core/logging");
// Base class for markers. All markers share the same GLSL, except for one
// function that defines the marker geometry.
var MarkerGLGlyph = /** @class */ (function (_super) {
    tslib_1.__extends(MarkerGLGlyph, _super);
    function MarkerGLGlyph() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MarkerGLGlyph.prototype.init = function () {
        var gl = this.gl;
        var vert = markers_vert_1.vertex_shader;
        var frag = markers_frag_1.fragment_shader(this._marker_code);
        // The program
        this.prog = new gloo2_1.Program(gl);
        this.prog.set_shaders(vert, frag);
        // Real attributes
        this.vbo_x = new gloo2_1.VertexBuffer(gl);
        this.prog.set_attribute('a_x', 'float', this.vbo_x);
        this.vbo_y = new gloo2_1.VertexBuffer(gl);
        this.prog.set_attribute('a_y', 'float', this.vbo_y);
        this.vbo_s = new gloo2_1.VertexBuffer(gl);
        this.prog.set_attribute('a_size', 'float', this.vbo_s);
        this.vbo_a = new gloo2_1.VertexBuffer(gl);
        this.prog.set_attribute('a_angle', 'float', this.vbo_a);
        // VBO's for attributes (they may not be used if value is singleton)
        this.vbo_linewidth = new gloo2_1.VertexBuffer(gl);
        this.vbo_fg_color = new gloo2_1.VertexBuffer(gl);
        this.vbo_bg_color = new gloo2_1.VertexBuffer(gl);
        this.index_buffer = new gloo2_1.IndexBuffer(gl);
    };
    MarkerGLGlyph.prototype.draw = function (indices, mainGlyph, trans) {
        // The main glyph has the data, *this* glyph has the visuals.
        var mainGlGlyph = mainGlyph.glglyph;
        var nvertices = mainGlGlyph.nvertices;
        // Upload data if we must. Only happens for main glyph.
        if (mainGlGlyph.data_changed) {
            if (!(isFinite(trans.dx) && isFinite(trans.dy))) {
                return; // not sure why, but it happens on init sometimes (#4367)
            }
            mainGlGlyph._baked_offset = [trans.dx, trans.dy]; // float32 precision workaround; used in _set_data() and below
            mainGlGlyph._set_data(nvertices);
            mainGlGlyph.data_changed = false;
        }
        else if (this.glyph instanceof circle_1.CircleView && this.glyph._radius != null &&
            (this.last_trans == null || trans.sx != this.last_trans.sx || trans.sy != this.last_trans.sy)) {
            // Keep screen radius up-to-date for circle glyph. Only happens when a radius is given
            this.last_trans = trans;
            this.vbo_s.set_data(0, new Float32Array(arrayable_1.map(this.glyph.sradius, function (s) { return s * 2; })));
        }
        // Update visuals if we must. Can happen for all glyphs.
        if (this.visuals_changed) {
            this._set_visuals(nvertices);
            this.visuals_changed = false;
        }
        // Handle transformation to device coordinates
        // Note the baked-in offset to avoid float32 precision problems
        var baked_offset = mainGlGlyph._baked_offset;
        this.prog.set_uniform('u_pixel_ratio', 'float', [trans.pixel_ratio]);
        this.prog.set_uniform('u_canvas_size', 'vec2', [trans.width, trans.height]);
        this.prog.set_uniform('u_offset', 'vec2', [trans.dx - baked_offset[0], trans.dy - baked_offset[1]]);
        this.prog.set_uniform('u_scale', 'vec2', [trans.sx, trans.sy]);
        // Select buffers from main glyph
        // (which may be this glyph but maybe not if this is a (non)selection glyph)
        this.prog.set_attribute('a_x', 'float', mainGlGlyph.vbo_x);
        this.prog.set_attribute('a_y', 'float', mainGlGlyph.vbo_y);
        this.prog.set_attribute('a_size', 'float', mainGlGlyph.vbo_s);
        this.prog.set_attribute('a_angle', 'float', mainGlGlyph.vbo_a);
        // Draw directly or using indices. Do not handle indices if they do not
        // fit in a uint16; WebGL 1.0 does not support uint32.
        if (indices.length == 0)
            return;
        else if (indices.length === nvertices)
            this.prog.draw(this.gl.POINTS, [0, nvertices]);
        else if (nvertices < 65535) {
            // On IE the marker size is reduced to 1 px when using an index buffer
            // A MS Edge dev on Twitter said on 24-04-2014: "gl_PointSize > 1.0 works
            // in DrawArrays; gl_PointSize > 1.0 in DrawElements is coming soon in the
            // next renderer update.
            var ua = window.navigator.userAgent;
            if ((ua.indexOf("MSIE ") + ua.indexOf("Trident/") + ua.indexOf("Edge/")) > 0) {
                logging_1.logger.warn('WebGL warning: IE is known to produce 1px sprites whith selections.');
            }
            this.index_buffer.set_size(indices.length * 2);
            this.index_buffer.set_data(0, new Uint16Array(indices));
            this.prog.draw(this.gl.POINTS, this.index_buffer);
        }
        else {
            // Work around the limit that the indexbuffer must be uint16. We draw in chunks.
            // First collect indices in chunks
            var chunksize = 64000; // 65536
            var chunks = [];
            for (var i = 0, end = Math.ceil(nvertices / chunksize); i < end; i++) {
                chunks.push([]);
            }
            for (var i = 0, end = indices.length; i < end; i++) {
                var uint16_index = indices[i] % chunksize;
                var chunk = Math.floor(indices[i] / chunksize);
                chunks[chunk].push(uint16_index);
            }
            // Then draw each chunk
            for (var chunk = 0, end = chunks.length; chunk < end; chunk++) {
                var these_indices = new Uint16Array(chunks[chunk]);
                var offset = chunk * chunksize * 4;
                if (these_indices.length === 0) {
                    continue;
                }
                this.prog.set_attribute('a_x', 'float', mainGlGlyph.vbo_x, 0, offset);
                this.prog.set_attribute('a_y', 'float', mainGlGlyph.vbo_y, 0, offset);
                this.prog.set_attribute('a_size', 'float', mainGlGlyph.vbo_s, 0, offset);
                this.prog.set_attribute('a_angle', 'float', mainGlGlyph.vbo_a, 0, offset);
                if (this.vbo_linewidth.used) {
                    this.prog.set_attribute('a_linewidth', 'float', this.vbo_linewidth, 0, offset);
                }
                if (this.vbo_fg_color.used) {
                    this.prog.set_attribute('a_fg_color', 'vec4', this.vbo_fg_color, 0, offset * 4);
                }
                if (this.vbo_bg_color.used) {
                    this.prog.set_attribute('a_bg_color', 'vec4', this.vbo_bg_color, 0, offset * 4);
                }
                // The actual drawing
                this.index_buffer.set_size(these_indices.length * 2);
                this.index_buffer.set_data(0, these_indices);
                this.prog.draw(this.gl.POINTS, this.index_buffer);
            }
        }
    };
    MarkerGLGlyph.prototype._set_data = function (nvertices) {
        var n = nvertices * 4; // in bytes
        // Set buffer size
        this.vbo_x.set_size(n);
        this.vbo_y.set_size(n);
        this.vbo_a.set_size(n);
        this.vbo_s.set_size(n);
        // Upload data for x and y, apply a baked-in offset for float32 precision (issue #3795)
        // The exact value for the baked_offset does not matter, as long as it brings the data to less extreme values
        var xx = new Float64Array(this.glyph._x);
        var yy = new Float64Array(this.glyph._y);
        for (var i = 0, end = nvertices; i < end; i++) {
            xx[i] += this._baked_offset[0];
            yy[i] += this._baked_offset[1];
        }
        this.vbo_x.set_data(0, new Float32Array(xx));
        this.vbo_y.set_data(0, new Float32Array(yy));
        // Angle if available; circle does not have angle. If we don't set data, angle is default 0 in glsl
        if (this.glyph._angle != null) {
            this.vbo_a.set_data(0, new Float32Array(this.glyph._angle));
        }
        // Radius is special; some markes allow radius in data-coords instead of screen coords
        // @radius tells us that radius is in units, sradius is the pre-calculated screen radius
        if (this.glyph instanceof circle_1.CircleView && this.glyph._radius != null)
            this.vbo_s.set_data(0, new Float32Array(arrayable_1.map(this.glyph.sradius, function (s) { return s * 2; })));
        else
            this.vbo_s.set_data(0, new Float32Array(this.glyph._size));
    };
    MarkerGLGlyph.prototype._set_visuals = function (nvertices) {
        base_1.attach_float(this.prog, this.vbo_linewidth, 'a_linewidth', nvertices, this.glyph.visuals.line, 'line_width');
        base_1.attach_color(this.prog, this.vbo_fg_color, 'a_fg_color', nvertices, this.glyph.visuals.line, 'line');
        base_1.attach_color(this.prog, this.vbo_bg_color, 'a_bg_color', nvertices, this.glyph.visuals.fill, 'fill');
        // Static value for antialias. Smaller aa-region to obtain crisper images
        this.prog.set_uniform('u_antialias', 'float', [0.8]);
    };
    return MarkerGLGlyph;
}(base_1.BaseGLGlyph));
exports.MarkerGLGlyph = MarkerGLGlyph;
function mk_marker(code) {
    return /** @class */ (function (_super) {
        tslib_1.__extends(class_1, _super);
        function class_1() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        Object.defineProperty(class_1.prototype, "_marker_code", {
            get: function () {
                return code;
            },
            enumerable: true,
            configurable: true
        });
        return class_1;
    }(MarkerGLGlyph));
}
var glsl = require("./markers.frag");
exports.CircleGLGlyph = mk_marker(glsl.circle);
exports.SquareGLGlyph = mk_marker(glsl.square);
exports.DiamondGLGlyph = mk_marker(glsl.diamond);
exports.TriangleGLGlyph = mk_marker(glsl.triangle);
exports.InvertedTriangleGLGlyph = mk_marker(glsl.invertedtriangle);
exports.HexGLGlyph = mk_marker(glsl.hex);
exports.CrossGLGlyph = mk_marker(glsl.cross);
exports.CircleCrossGLGlyph = mk_marker(glsl.circlecross);
exports.SquareCrossGLGlyph = mk_marker(glsl.squarecross);
exports.DiamondCrossGLGlyph = mk_marker(glsl.diamondcross);
exports.XGLGlyph = mk_marker(glsl.x);
exports.CircleXGLGlyph = mk_marker(glsl.circlex);
exports.SquareXGLGlyph = mk_marker(glsl.squarex);
exports.AsteriskGLGlyph = mk_marker(glsl.asterisk);
