import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { PointGeometry, SpanGeometry } from "core/geometry";
import { LineMixinVector } from "core/property_mixins";
import * as visuals from "core/visuals";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
export interface LineData extends XYGlyphData {
}
export interface LineView extends LineData {
}
export declare class LineView extends XYGlyphView {
    model: Line;
    visuals: Line.Visuals;
    protected _render(ctx: Context2d, indices: number[], { sx, sy }: LineData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _hit_span(geometry: SpanGeometry): Selection;
    get_interpolation_hit(i: number, geometry: PointGeometry | SpanGeometry): [number, number];
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace Line {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
    }
    interface Props extends XYGlyph.Props {
    }
    interface Visuals extends XYGlyph.Visuals {
        line: visuals.Line;
    }
}
export interface Line extends Line.Attrs {
}
export declare class Line extends XYGlyph {
    properties: Line.Props;
    constructor(attrs?: Partial<Line.Attrs>);
    static initClass(): void;
}
