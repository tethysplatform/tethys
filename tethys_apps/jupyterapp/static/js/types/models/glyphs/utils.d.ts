import { Visuals, Line, Fill } from "core/visuals";
import { Context2d } from "core/util/canvas";
import { IBBox } from "core/util/bbox";
import { PointGeometry, SpanGeometry } from "core/geometry";
import { GlyphRendererView } from "../renderers/glyph_renderer";
export declare function generic_line_legend(visuals: Visuals & {
    line: Line;
}, ctx: Context2d, { x0, x1, y0, y1 }: IBBox, index: number): void;
export declare function generic_area_legend(visuals: {
    line: Line;
    fill: Fill;
}, ctx: Context2d, { x0, x1, y0, y1 }: IBBox, index: number): void;
export declare function line_interpolation(renderer: GlyphRendererView, geometry: PointGeometry | SpanGeometry, x2: number, y2: number, x3: number, y3: number): [number, number];
