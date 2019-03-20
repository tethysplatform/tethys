import { PointGeometry, SpanGeometry } from "core/geometry";
import { NumberSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import { IBBox } from "core/util/bbox";
import { SpatialIndex } from "core/util/spatial";
import { Context2d } from "core/util/canvas";
import { Glyph, GlyphView, GlyphData } from "./glyph";
import { Selection } from "../selections/selection";
export interface SegmentData extends GlyphData {
    _x0: Arrayable<number>;
    _y0: Arrayable<number>;
    _x1: Arrayable<number>;
    _y1: Arrayable<number>;
    sx0: Arrayable<number>;
    sy0: Arrayable<number>;
    sx1: Arrayable<number>;
    sy1: Arrayable<number>;
}
export interface SegmentView extends SegmentData {
}
export declare class SegmentView extends GlyphView {
    model: Segment;
    visuals: Segment.Visuals;
    protected _index_data(): SpatialIndex;
    protected _render(ctx: Context2d, indices: number[], { sx0, sy0, sx1, sy1 }: SegmentData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _hit_span(geometry: SpanGeometry): Selection;
    scenterx(i: number): number;
    scentery(i: number): number;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace Segment {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends Glyph.Attrs, Mixins {
        x0: NumberSpec;
        y0: NumberSpec;
        x1: NumberSpec;
        y1: NumberSpec;
    }
    interface Props extends Glyph.Props {
    }
    interface Visuals extends Glyph.Visuals {
        line: Line;
    }
}
export interface Segment extends Segment.Attrs {
}
export declare class Segment extends Glyph {
    properties: Segment.Props;
    constructor(attrs?: Partial<Segment.Attrs>);
    static initClass(): void;
}
