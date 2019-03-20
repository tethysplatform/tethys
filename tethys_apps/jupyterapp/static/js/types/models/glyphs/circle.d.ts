import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { PointGeometry, SpanGeometry, RectGeometry, PolyGeometry } from "core/geometry";
import { DistanceSpec, AngleSpec } from "core/vectorization";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
export interface CircleData extends XYGlyphData {
    _angle: Arrayable<number>;
    _size: Arrayable<number>;
    _radius?: Arrayable<number>;
    sradius: Arrayable<number>;
    max_size: number;
    max_radius: number;
}
export interface CircleView extends CircleData {
}
export declare class CircleView extends XYGlyphView {
    model: Circle;
    visuals: Circle.Visuals;
    protected _map_data(): void;
    protected _mask_data(): number[];
    protected _render(ctx: Context2d, indices: number[], { sx, sy, sradius }: CircleData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _hit_span(geometry: SpanGeometry): Selection;
    protected _hit_rect(geometry: RectGeometry): Selection;
    protected _hit_poly(geometry: PolyGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, { x0, y0, x1, y1 }: IBBox, index: number): void;
}
export declare namespace Circle {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        angle: AngleSpec;
        size: DistanceSpec;
        radius: DistanceSpec | null;
        radius_dimension: "x" | "y";
    }
    interface Props extends XYGlyph.Props {
        angle: p.AngleSpec;
        size: p.DistanceSpec;
        radius: p.DistanceSpec;
        radius_dimension: p.Property<"x" | "y">;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface Circle extends Circle.Attrs {
}
export declare class Circle extends XYGlyph {
    properties: Circle.Props;
    constructor(attrs?: Partial<Circle.Attrs>);
    static initClass(): void;
    initialize(): void;
}
