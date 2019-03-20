"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var gloo2_1 = require("gloo2");
var base_1 = require("./base");
var line_vert_1 = require("./line.vert");
var line_frag_1 = require("./line.frag");
var color_1 = require("core/util/color");
var DashAtlas = /** @class */ (function () {
    function DashAtlas(gl) {
        this._atlas = {};
        this._index = 0;
        this._width = 256;
        this._height = 256;
        // Init texture
        this.tex = new gloo2_1.Texture2D(gl);
        this.tex.set_wrapping(gl.REPEAT, gl.REPEAT);
        this.tex.set_interpolation(gl.NEAREST, gl.NEAREST);
        this.tex.set_size([this._height, this._width], gl.RGBA);
        this.tex.set_data([0, 0], [this._height, this._width], new Uint8Array(this._height * this._width * 4));
        // Init with solid line (index 0 is reserved for this)
        this.get_atlas_data([1]);
    }
    DashAtlas.prototype.get_atlas_data = function (pattern) {
        var key = pattern.join('-');
        var findex_period = this._atlas[key];
        if (findex_period === undefined) {
            var _a = this.make_pattern(pattern), data = _a[0], period = _a[1];
            this.tex.set_data([this._index, 0], [1, this._width], new Uint8Array(data.map(function (x) { return x + 10; })));
            this._atlas[key] = [this._index / this._height, period];
            this._index += 1;
        }
        return this._atlas[key];
    };
    DashAtlas.prototype.make_pattern = function (pattern) {
        // A pattern is defined as on/off sequence of segments
        // It must be a multiple of 2
        if (pattern.length > 1 && pattern.length % 2) {
            pattern = pattern.concat(pattern);
        }
        // Period is sum of elements
        var period = 0;
        for (var _i = 0, pattern_1 = pattern; _i < pattern_1.length; _i++) {
            var v = pattern_1[_i];
            period += v;
        }
        // Find all start and end of on-segment only
        var C = [];
        var c = 0;
        for (var i = 0, end = pattern.length + 2; i < end; i += 2) {
            var a = Math.max(0.0001, pattern[i % pattern.length]);
            var b = Math.max(0.0001, pattern[(i + 1) % pattern.length]);
            C.push(c, c + a);
            c += a + b;
        }
        // Build pattern
        var n = this._width;
        var Z = new Float32Array(n * 4);
        for (var i = 0, end = n; i < end; i++) {
            var dash_end = void 0, dash_start = void 0, dash_type = void 0;
            var x = (period * i) / (n - 1);
            // get index at min - index = np.argmin(abs(C-(x)))
            var index = 0;
            var val_at_index = 1e16;
            for (var j = 0, endj = C.length; j < endj; j++) {
                var val = Math.abs(C[j] - x);
                if (val < val_at_index) {
                    index = j;
                    val_at_index = val;
                }
            }
            if ((index % 2) === 0) {
                dash_type = (x <= C[index]) ? +1 : 0;
                dash_start = C[index];
                dash_end = C[index + 1];
            }
            else {
                dash_type = (x > C[index]) ? -1 : 0;
                dash_start = C[index - 1];
                dash_end = C[index];
            }
            Z[(i * 4) + 0] = C[index];
            Z[(i * 4) + 1] = dash_type;
            Z[(i * 4) + 2] = dash_start;
            Z[(i * 4) + 3] = dash_end;
        }
        return [Z, period];
    };
    return DashAtlas;
}());
var joins = { miter: 0, round: 1, bevel: 2 };
var caps = {
    '': 0, none: 0, '.': 0,
    round: 1, ')': 1, '(': 1, o: 1,
    'triangle in': 2, '<': 2,
    'triangle out': 3, '>': 3,
    square: 4, '[': 4, ']': 4, '=': 4,
    butt: 5, '|': 5,
};
var LineGLGlyph = /** @class */ (function (_super) {
    tslib_1.__extends(LineGLGlyph, _super);
    function LineGLGlyph() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    LineGLGlyph.prototype.init = function () {
        var gl = this.gl;
        this._scale_aspect = 0; // keep track, so we know when we need to update segment data
        var vert = line_vert_1.vertex_shader;
        var frag = line_frag_1.fragment_shader;
        // The program
        this.prog = new gloo2_1.Program(gl);
        this.prog.set_shaders(vert, frag);
        this.index_buffer = new gloo2_1.IndexBuffer(gl);
        // Buffers
        this.vbo_position = new gloo2_1.VertexBuffer(gl);
        this.vbo_tangents = new gloo2_1.VertexBuffer(gl);
        this.vbo_segment = new gloo2_1.VertexBuffer(gl);
        this.vbo_angles = new gloo2_1.VertexBuffer(gl);
        this.vbo_texcoord = new gloo2_1.VertexBuffer(gl);
        // Dash atlas
        this.dash_atlas = new DashAtlas(gl);
    };
    LineGLGlyph.prototype.draw = function (indices, mainGlyph, trans) {
        var mainGlGlyph = mainGlyph.glglyph;
        if (mainGlGlyph.data_changed) {
            if (!(isFinite(trans.dx) && isFinite(trans.dy))) {
                return; // not sure why, but it happens on init sometimes (#4367)
            }
            mainGlGlyph._baked_offset = [trans.dx, trans.dy]; // float32 precision workaround; used in _bake() and below
            mainGlGlyph._set_data();
            mainGlGlyph.data_changed = false;
        }
        if (this.visuals_changed) {
            this._set_visuals();
            this.visuals_changed = false;
        }
        // Decompose x-y scale into scalar scale and aspect-vector.
        var sx = trans.sx, sy = trans.sy;
        var scale_length = Math.sqrt(sx * sx + sy * sy);
        sx /= scale_length;
        sy /= scale_length;
        // Do we need to re-calculate segment data and cumsum?
        if (Math.abs(this._scale_aspect - sy / sx) > Math.abs(1e-3 * this._scale_aspect)) {
            mainGlGlyph._update_scale(sx, sy);
            this._scale_aspect = sy / sx;
        }
        // Select buffers from main glyph
        // (which may be this glyph but maybe not if this is a (non)selection glyph)
        this.prog.set_attribute('a_position', 'vec2', mainGlGlyph.vbo_position);
        this.prog.set_attribute('a_tangents', 'vec4', mainGlGlyph.vbo_tangents);
        this.prog.set_attribute('a_segment', 'vec2', mainGlGlyph.vbo_segment);
        this.prog.set_attribute('a_angles', 'vec2', mainGlGlyph.vbo_angles);
        this.prog.set_attribute('a_texcoord', 'vec2', mainGlGlyph.vbo_texcoord);
        //
        this.prog.set_uniform('u_length', 'float', [mainGlGlyph.cumsum]);
        this.prog.set_texture('u_dash_atlas', this.dash_atlas.tex);
        // Handle transformation to device coordinates
        var baked_offset = mainGlGlyph._baked_offset;
        this.prog.set_uniform('u_pixel_ratio', 'float', [trans.pixel_ratio]);
        this.prog.set_uniform('u_canvas_size', 'vec2', [trans.width, trans.height]);
        this.prog.set_uniform('u_offset', 'vec2', [trans.dx - baked_offset[0], trans.dy - baked_offset[1]]);
        this.prog.set_uniform('u_scale_aspect', 'vec2', [sx, sy]);
        this.prog.set_uniform('u_scale_length', 'float', [scale_length]);
        this.I_triangles = mainGlGlyph.I_triangles;
        if (this.I_triangles.length < 65535) {
            // Data is small enough to draw in one pass
            this.index_buffer.set_size(this.I_triangles.length * 2);
            this.index_buffer.set_data(0, new Uint16Array(this.I_triangles));
            this.prog.draw(this.gl.TRIANGLES, this.index_buffer);
            // @prog.draw(@gl.LINE_STRIP, @index_buffer)  # Use this to draw the line skeleton
        }
        else {
            // Work around the limit that the indexbuffer must be uint16. We draw in chunks.
            // First collect indices in chunks
            indices = Array.from(this.I_triangles);
            var nvertices = this.I_triangles.length;
            var chunksize = 64008; // 65536 max. 64008 is divisible by 12
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
                this.prog.set_attribute('a_position', 'vec2', mainGlGlyph.vbo_position, 0, offset * 2);
                this.prog.set_attribute('a_tangents', 'vec4', mainGlGlyph.vbo_tangents, 0, offset * 4);
                this.prog.set_attribute('a_segment', 'vec2', mainGlGlyph.vbo_segment, 0, offset * 2);
                this.prog.set_attribute('a_angles', 'vec2', mainGlGlyph.vbo_angles, 0, offset * 2);
                this.prog.set_attribute('a_texcoord', 'vec2', mainGlGlyph.vbo_texcoord, 0, offset * 2);
                // The actual drawing
                this.index_buffer.set_size(these_indices.length * 2);
                this.index_buffer.set_data(0, these_indices);
                this.prog.draw(this.gl.TRIANGLES, this.index_buffer);
            }
        }
    };
    LineGLGlyph.prototype._set_data = function () {
        this._bake();
        this.vbo_position.set_size(this.V_position.length * 4);
        this.vbo_position.set_data(0, this.V_position);
        this.vbo_tangents.set_size(this.V_tangents.length * 4);
        this.vbo_tangents.set_data(0, this.V_tangents);
        this.vbo_angles.set_size(this.V_angles.length * 4);
        this.vbo_angles.set_data(0, this.V_angles);
        this.vbo_texcoord.set_size(this.V_texcoord.length * 4);
        this.vbo_texcoord.set_data(0, this.V_texcoord);
    };
    LineGLGlyph.prototype._set_visuals = function () {
        var _a;
        var color = color_1.color2rgba(this.glyph.visuals.line.line_color.value(), this.glyph.visuals.line.line_alpha.value());
        var cap = caps[this.glyph.visuals.line.line_cap.value()];
        var join = joins[this.glyph.visuals.line.line_join.value()];
        this.prog.set_uniform('u_color', 'vec4', color);
        this.prog.set_uniform('u_linewidth', 'float', [this.glyph.visuals.line.line_width.value()]);
        this.prog.set_uniform('u_antialias', 'float', [0.9]); // Smaller aa-region to obtain crisper images
        this.prog.set_uniform('u_linecaps', 'vec2', [cap, cap]);
        this.prog.set_uniform('u_linejoin', 'float', [join]);
        this.prog.set_uniform('u_miter_limit', 'float', [10.0]); // 10 should be a good value
        // https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-miterlimit
        var dash_pattern = this.glyph.visuals.line.line_dash.value();
        var dash_index = 0;
        var dash_period = 1;
        if (dash_pattern.length) {
            _a = this.dash_atlas.get_atlas_data(dash_pattern), dash_index = _a[0], dash_period = _a[1];
        }
        this.prog.set_uniform('u_dash_index', 'float', [dash_index]); // 0 means solid line
        this.prog.set_uniform('u_dash_phase', 'float', [this.glyph.visuals.line.line_dash_offset.value()]);
        this.prog.set_uniform('u_dash_period', 'float', [dash_period]);
        this.prog.set_uniform('u_dash_caps', 'vec2', [cap, cap]);
        this.prog.set_uniform('u_closed', 'float', [0]); // We dont do closed lines
    };
    LineGLGlyph.prototype._bake = function () {
        // This is what you get if you port 50 lines of numpy code to JS.
        // V_segment is handled in another method, because it depends on the aspect
        // ratio of the scale (The original paper/code assumed isotropic scaling).
        //
        // Buffer dtype from the Python implementation:
        //
        // self.vtype = np.dtype( [('a_position', 'f4', 2),
        //                         ('a_segment',  'f4', 2),
        //                         ('a_angles',   'f4', 2),
        //                         ('a_tangents', 'f4', 4),
        //                         ('a_texcoord', 'f4', 2) ])
        // Init array of implicit shape nx2
        var I, T, V_angles2, V_position2, V_tangents2, V_texcoord2, Vp, Vt;
        var n = this.nvertices;
        var _x = new Float64Array(this.glyph._x);
        var _y = new Float64Array(this.glyph._y);
        // Init vertex data
        var V_position = (Vp = new Float32Array(n * 2));
        //V_segment = new Float32Array(n*2)  # Done later
        var V_angles = new Float32Array(n * 2);
        var V_tangents = (Vt = new Float32Array(n * 4)); // mind the 4!
        // Position
        for (var i = 0, end = n; i < end; i++) {
            V_position[(i * 2) + 0] = _x[i] + this._baked_offset[0];
            V_position[(i * 2) + 1] = _y[i] + this._baked_offset[1];
        }
        // Tangents & norms (need tangents to calculate segments based on scale)
        this.tangents = (T = new Float32Array((n * 2) - 2));
        for (var i = 0, end = n - 1; i < end; i++) {
            T[(i * 2) + 0] = Vp[((i + 1) * 2) + 0] - Vp[(i * 2) + 0];
            T[(i * 2) + 1] = Vp[((i + 1) * 2) + 1] - Vp[(i * 2) + 1];
        }
        for (var i = 0, end = n - 1; i < end; i++) {
            // V['a_tangents'][+1:, :2] = T
            V_tangents[((i + 1) * 4) + 0] = T[(i * 2) + 0];
            V_tangents[((i + 1) * 4) + 1] = T[(i * 2) + 1];
            // V['a_tangents'][:-1, 2:] = T
            V_tangents[(i * 4) + 2] = T[(i * 2) + 0];
            V_tangents[(i * 4) + 3] = T[(i * 2) + 1];
        }
        // V['a_tangents'][0  , :2] = T[0]
        V_tangents[(0 * 4) + 0] = T[0];
        V_tangents[(0 * 4) + 1] = T[1];
        // V['a_tangents'][ -1, 2:] = T[-1]
        V_tangents[((n - 1) * 4) + 2] = T[((n - 2) * 2) + 0];
        V_tangents[((n - 1) * 4) + 3] = T[((n - 2) * 2) + 1];
        // Angles
        var A = new Float32Array(n);
        for (var i = 0, end = n; i < end; i++) {
            A[i] = Math.atan2((Vt[(i * 4) + 0] * Vt[(i * 4) + 3]) - (Vt[(i * 4) + 1] * Vt[(i * 4) + 2]), (Vt[(i * 4) + 0] * Vt[(i * 4) + 2]) + (Vt[(i * 4) + 1] * Vt[(i * 4) + 3]));
        }
        for (var i = 0, end = n - 1; i < end; i++) {
            V_angles[(i * 2) + 0] = A[i];
            V_angles[(i * 2) + 1] = A[i + 1];
        }
        // Step 1: A -- B -- C  =>  A -- B, B' -- C
        // Repeat our array 4 times
        var m = (4 * n) - 4;
        this.V_position = (V_position2 = new Float32Array(m * 2));
        this.V_angles = (V_angles2 = new Float32Array(m * 2));
        this.V_tangents = (V_tangents2 = new Float32Array(m * 4)); // mind the 4!
        this.V_texcoord = (V_texcoord2 = new Float32Array(m * 2));
        var o = 2;
        //
        // Arg, we really need an ndarray thing in JS :/
        for (var i = 0, end = n; i < end; i++) { // all nodes on the line
            for (var j = 0; j < 4; j++) { // the four quad vertices
                for (var k = 0; k < 2; k++) { // xy
                    V_position2[((((i * 4) + j) - o) * 2) + k] = V_position[(i * 2) + k];
                    V_angles2[(((i * 4) + j) * 2) + k] = V_angles[(i * 2) + k];
                } // no offset
                for (var k = 0; k < 4; k++) {
                    V_tangents2[((((i * 4) + j) - o) * 4) + k] = V_tangents[(i * 4) + k];
                }
            }
        }
        for (var i = 0, end = n; i < end; i++) {
            V_texcoord2[(((i * 4) + 0) * 2) + 0] = -1;
            V_texcoord2[(((i * 4) + 1) * 2) + 0] = -1;
            V_texcoord2[(((i * 4) + 2) * 2) + 0] = +1;
            V_texcoord2[(((i * 4) + 3) * 2) + 0] = +1;
            //
            V_texcoord2[(((i * 4) + 0) * 2) + 1] = -1;
            V_texcoord2[(((i * 4) + 1) * 2) + 1] = +1;
            V_texcoord2[(((i * 4) + 2) * 2) + 1] = -1;
            V_texcoord2[(((i * 4) + 3) * 2) + 1] = +1;
        }
        // Indices
        //I = np.resize( np.array([0,1,2,1,2,3], dtype=np.uint32), (n-1)*(2*3))
        //I += np.repeat( 4*np.arange(n-1), 6)
        var ni = (n - 1) * 6;
        this.I_triangles = (I = new Uint32Array(ni));
        // Order of indices is such that drawing as line_strip reveals the line skeleton
        // Might have implications on culling, if we ever turn that on.
        // Order in paper was: 0 1 2 1 2 3
        for (var i = 0, end = n; i < end; i++) {
            I[(i * 6) + 0] = 0 + (4 * i);
            I[(i * 6) + 1] = 1 + (4 * i);
            I[(i * 6) + 2] = 3 + (4 * i);
            I[(i * 6) + 3] = 2 + (4 * i);
            I[(i * 6) + 4] = 0 + (4 * i);
            I[(i * 6) + 5] = 3 + (4 * i);
        }
    };
    LineGLGlyph.prototype._update_scale = function (sx, sy) {
        // Update segment data and cumsum so the length along the line has the
        // scale aspect ratio in it. In the vertex shader we multiply with the
        // "isotropic part" of the scale.
        var V_segment2;
        var n = this.nvertices;
        var m = (4 * n) - 4;
        // Prepare arrays
        var T = this.tangents;
        var N = new Float32Array(n - 1);
        var V_segment = new Float32Array(n * 2); // Elements are initialized with 0
        this.V_segment = (V_segment2 = new Float32Array(m * 2));
        // Calculate vector lengths - with scale aspect ratio taken into account
        for (var i = 0, end = n - 1; i < end; i++) {
            N[i] = Math.sqrt(Math.pow(T[(i * 2) + 0] * sx, 2) + Math.pow(T[(i * 2) + 1] * sy, 2));
        }
        // Calculate Segments
        var cumsum = 0;
        for (var i = 0, end = n - 1; i < end; i++) {
            cumsum += N[i];
            V_segment[((i + 1) * 2) + 0] = cumsum;
            V_segment[(i * 2) + 1] = cumsum;
        }
        // Upscale (same loop as in _bake())
        for (var i = 0, end = n; i < end; i++) {
            for (var j = 0; j < 4; j++) {
                for (var k = 0; k < 2; k++) {
                    V_segment2[(((i * 4) + j) * 2) + k] = V_segment[(i * 2) + k];
                }
            }
        }
        // Update
        this.cumsum = cumsum; // L[-1] in Nico's code
        this.vbo_segment.set_size(this.V_segment.length * 4);
        this.vbo_segment.set_data(0, this.V_segment);
    };
    return LineGLGlyph;
}(base_1.BaseGLGlyph));
exports.LineGLGlyph = LineGLGlyph;
