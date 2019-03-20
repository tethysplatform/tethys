import { IBBox } from "core/util/bbox";
import { SpatialIndex } from "core/util/spatial";
import { PointGeometry, SpanGeometry } from "core/geometry";
import { NumberSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import { Context2d } from "core/util/canvas";
import { Glyph, GlyphView, GlyphData } from "./glyph";
import { Selection } from "../selections/selection";
export interface MultiLineData extends GlyphData {
    _xs: Arrayable<Arrayable<number>>;
    _ys: Arrayable<Arrayable<number>>;
    sxs: Arrayable<Arrayable<number>>;
    sys: Arrayable<Arrayable<number>>;
}
export interface MultiLineView extends MultiLineData {
}
export declare class MultiLineView extends GlyphView {
    model: MultiLine;
    visuals: MultiLine.Visuals;
    protected _index_data(): SpatialIndex;
    protected _render(ctx: Context2d, indices: number[], { sxs, sys }: MultiLineData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _hit_span(geometry: SpanGeometry): Selection;
    get_interpolation_hit(i: number, point_i: number, geometry: PointGeometry | SpanGeometry): [number, number];
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
    scenterx(): number;
    scentery(): number;
}
export declare namespace MultiLine {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends Glyph.Attrs, Mixins {
        xs: NumberSpec;
        ys: NumberSpec;
    }
    interface Props extends Glyph.Props {
    }
    interface Visuals extends Glyph.Visuals {
        line: Line;
    }
}
export interface MultiLine extends MultiLine.Attrs {
}
export declare class MultiLine extends Glyph {
    properties: MultiLine.Props;
    constructor(attrs?: Partial<MultiLine.Attrs>);
    static initClass(): void;
}
