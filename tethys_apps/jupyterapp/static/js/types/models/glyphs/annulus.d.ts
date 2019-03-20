import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { Arrayable } from "core/types";
import { PointGeometry } from "core/geometry";
import { DistanceSpec } from "core/vectorization";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import * as p from "core/properties";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
export interface AnnulusData extends XYGlyphData {
    _inner_radius: Arrayable<number>;
    _outer_radius: Arrayable<number>;
    sinner_radius: Arrayable<number>;
    souter_radius: Arrayable<number>;
    max_inner_radius: number;
    max_outer_radius: number;
}
export interface AnnulusView extends AnnulusData {
}
export declare class AnnulusView extends XYGlyphView {
    model: Annulus;
    visuals: Annulus.Visuals;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, sinner_radius, souter_radius }: AnnulusData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, { x0, y0, x1, y1 }: IBBox, index: number): void;
}
export declare namespace Annulus {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        inner_radius: DistanceSpec;
        outer_radius: DistanceSpec;
    }
    interface Props extends XYGlyph.Props {
        inner_radius: p.DistanceSpec;
        outer_radius: p.DistanceSpec;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface Annulus extends Annulus.Attrs {
}
export declare class Annulus extends XYGlyph {
    properties: Annulus.Props;
    constructor(attrs?: Partial<Annulus.Attrs>);
    static initClass(): void;
}
