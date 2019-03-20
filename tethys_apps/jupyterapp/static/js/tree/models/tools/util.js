"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var array_1 = require("core/util/array");
var glyph_renderer_1 = require("../renderers/glyph_renderer");
var graph_renderer_1 = require("../renderers/graph_renderer");
function compute_renderers(renderers, all_renderers, names) {
    if (renderers == null)
        return [];
    var result;
    if (renderers == 'auto') {
        result = all_renderers.filter(function (r) {
            return r instanceof glyph_renderer_1.GlyphRenderer || r instanceof graph_renderer_1.GraphRenderer;
        });
    }
    else
        result = renderers;
    if (names.length > 0)
        result = result.filter(function (r) { return array_1.includes(names, r.name); });
    return result;
}
exports.compute_renderers = compute_renderers;
