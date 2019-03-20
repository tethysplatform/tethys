import { NumberSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import { IBBox } from "core/util/bbox";
import { SpatialIndex } from "core/util/spatial";
import { Context2d } from "core/util/canvas";
import { Glyph, GlyphView, GlyphData } from "./glyph";
export interface QuadraticData extends GlyphData {
    _x0: Arrayable<number>;
    _y0: Arrayable<number>;
    _x1: Arrayable<number>;
    _y1: Arrayable<number>;
    _cx: Arrayable<number>;
    _cy: Arrayable<number>;
    sx0: Arrayable<number>;
    sy0: Arrayable<number>;
    sx1: Arrayable<number>;
    sy1: Arrayable<number>;
    scx: Arrayable<number>;
    scy: Arrayable<number>;
}
export interface QuadraticView extends QuadraticData {
}
export declare class QuadraticView extends GlyphView {
    model: Quadratic;
    visuals: Quadratic.Visuals;
    protected _index_data(): SpatialIndex;
    protected _render(ctx: Context2d, indices: number[], { sx0, sy0, sx1, sy1, scx, scy }: QuadraticData): void;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
    scenterx(): number;
    scentery(): number;
}
export declare namespace Quadratic {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends Glyph.Attrs, Mixins {
        x0: NumberSpec;
        y0: NumberSpec;
        x1: NumberSpec;
        y1: NumberSpec;
        cx: NumberSpec;
        cy: NumberSpec;
    }
    interface Props extends Glyph.Props {
    }
    interface Visuals extends Glyph.Visuals {
        line: Line;
    }
}
export interface Quadratic extends Quadratic.Attrs {
}
export declare class Quadratic extends Glyph {
    properties: Quadratic.Props;
    constructor(attrs?: Partial<Quadratic.Attrs>);
    static initClass(): void;
}
