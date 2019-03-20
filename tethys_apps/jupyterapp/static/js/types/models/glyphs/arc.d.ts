import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { DistanceSpec, AngleSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import { Direction } from "core/enums";
import * as p from "core/properties";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
export interface ArcData extends XYGlyphData {
    _radius: Arrayable<number>;
    _start_angle: Arrayable<number>;
    _end_angle: Arrayable<number>;
    sradius: Arrayable<number>;
    max_radius: number;
}
export interface ArcView extends ArcData {
}
export declare class ArcView extends XYGlyphView {
    model: Arc;
    visuals: Arc.Visuals;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, sradius, _start_angle, _end_angle }: ArcData): void;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace Arc {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        direction: Direction;
        radius: DistanceSpec;
        start_angle: AngleSpec;
        end_angle: AngleSpec;
    }
    interface Props extends XYGlyph.Props {
        direction: p.Property<Direction>;
        radius: p.DistanceSpec;
        start_angle: p.AngleSpec;
        end_angle: p.AngleSpec;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
    }
}
export interface Arc extends Arc.Attrs {
}
export declare class Arc extends XYGlyph {
    properties: Arc.Props;
    constructor(attrs?: Partial<Arc.Attrs>);
    static initClass(): void;
}
