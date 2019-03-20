import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { DistanceSpec, AngleSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
export interface RayData extends XYGlyphData {
    _length: Arrayable<number>;
    _angle: Arrayable<number>;
    slength: Arrayable<number>;
}
export interface RayView extends RayData {
}
export declare class RayView extends XYGlyphView {
    model: Ray;
    visuals: Ray.Visuals;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, slength, _angle }: RayData): void;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace Ray {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        length: DistanceSpec;
        angle: AngleSpec;
    }
    interface Props extends XYGlyph.Props {
        length: p.DistanceSpec;
        angle: p.AngleSpec;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
    }
}
export interface Ray extends Ray.Attrs {
}
export declare class Ray extends XYGlyph {
    properties: Ray.Props;
    constructor(attrs?: Partial<Ray.Attrs>);
    static initClass(): void;
}
