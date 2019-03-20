import { Arrayable } from "core/types";
import { NumberSpec } from "core/vectorization";
import { SpatialIndex } from "core/util/spatial";
import { Glyph, GlyphView, GlyphData } from "./glyph";
export interface XYGlyphData extends GlyphData {
    _x: Arrayable<number>;
    _y: Arrayable<number>;
    sx: Arrayable<number>;
    sy: Arrayable<number>;
}
export interface XYGlyphView extends XYGlyphData {
}
export declare abstract class XYGlyphView extends GlyphView {
    model: XYGlyph;
    visuals: XYGlyph.Visuals;
    protected _index_data(): SpatialIndex;
    scenterx(i: number): number;
    scentery(i: number): number;
}
export declare namespace XYGlyph {
    interface Attrs extends Glyph.Attrs {
        x: NumberSpec;
        y: NumberSpec;
    }
    interface Props extends Glyph.Props {
    }
    interface Visuals extends Glyph.Visuals {
    }
}
export interface XYGlyph extends XYGlyph.Attrs {
}
export declare abstract class XYGlyph extends Glyph {
    properties: XYGlyph.Props;
    constructor(attrs?: Partial<XYGlyph.Attrs>);
    static initClass(): void;
}
