import { NumberSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import { IBBox } from "core/util/bbox";
import { SpatialIndex } from "core/util/spatial";
import { Context2d } from "core/util/canvas";
import { Glyph, GlyphView, GlyphData } from "./glyph";
export interface BezierData extends GlyphData {
    _x0: Arrayable<number>;
    _y0: Arrayable<number>;
    _x1: Arrayable<number>;
    _y1: Arrayable<number>;
    _cx0: Arrayable<number>;
    _cy0: Arrayable<number>;
    _cx1: Arrayable<number>;
    _cy1: Arrayable<number>;
    sx0: Arrayable<number>;
    sy0: Arrayable<number>;
    sx1: Arrayable<number>;
    sy1: Arrayable<number>;
    scx0: Arrayable<number>;
    scy0: Arrayable<number>;
    scx1: Arrayable<number>;
    scy1: Arrayable<number>;
}
export interface BezierView extends BezierData {
}
export declare class BezierView extends GlyphView {
    model: Bezier;
    visuals: Bezier.Visuals;
    protected _index_data(): SpatialIndex;
    protected _render(ctx: Context2d, indices: number[], { sx0, sy0, sx1, sy1, scx0, scy0, scx1, scy1 }: BezierData): void;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
    scenterx(): number;
    scentery(): number;
}
export declare namespace Bezier {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends Glyph.Attrs, Mixins {
        x0: NumberSpec;
        y0: NumberSpec;
        x1: NumberSpec;
        y1: NumberSpec;
        cx0: NumberSpec;
        cy0: NumberSpec;
        cx1: NumberSpec;
        cy1: NumberSpec;
    }
    interface Props extends Glyph.Props {
    }
    interface Visuals extends Glyph.Visuals {
        line: Line;
    }
}
export interface Bezier extends Bezier.Attrs {
}
export declare class Bezier extends Glyph {
    properties: Bezier.Props;
    constructor(attrs?: Partial<Bezier.Attrs>);
    static initClass(): void;
}
