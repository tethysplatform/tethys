import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { PointGeometry } from "core/geometry";
import { DistanceSpec, AngleSpec } from "core/vectorization";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Arrayable } from "core/types";
import { Direction } from "core/enums";
import { Line, Fill } from "core/visuals";
import * as p from "core/properties";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
export interface AnnularWedgeData extends XYGlyphData {
    _inner_radius: Arrayable<number>;
    _outer_radius: Arrayable<number>;
    _start_angle: Arrayable<number>;
    _end_angle: Arrayable<number>;
    _angle: Arrayable<number>;
    sinner_radius: Arrayable<number>;
    souter_radius: Arrayable<number>;
    max_inner_radius: number;
    max_outer_radius: number;
}
export interface AnnularWedgeView extends AnnularWedgeData {
}
export declare class AnnularWedgeView extends XYGlyphView {
    model: AnnularWedge;
    visuals: AnnularWedge.Visuals;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, _start_angle, _angle, sinner_radius, souter_radius }: AnnularWedgeData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
    private _scenterxy;
    scenterx(i: number): number;
    scentery(i: number): number;
}
export declare namespace AnnularWedge {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        direction: Direction;
        inner_radius: DistanceSpec;
        outer_radius: DistanceSpec;
        start_angle: AngleSpec;
        end_angle: AngleSpec;
    }
    interface Props extends XYGlyph.Props {
        direction: p.Direction;
        inner_radius: p.DistanceSpec;
        outer_radius: p.DistanceSpec;
        start_angle: p.AngleSpec;
        end_angle: p.AngleSpec;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface AnnularWedge extends AnnularWedge.Attrs {
}
export declare class AnnularWedge extends XYGlyph {
    properties: AnnularWedge.Props;
    constructor(attrs?: Partial<AnnularWedge.Attrs>);
    static initClass(): void;
}
