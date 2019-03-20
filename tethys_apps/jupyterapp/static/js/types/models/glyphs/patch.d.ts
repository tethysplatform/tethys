import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
export interface PatchData extends XYGlyphData {
}
export interface PatchView extends PatchData {
}
export declare class PatchView extends XYGlyphView {
    model: Patch;
    visuals: Patch.Visuals;
    protected _render(ctx: Context2d, indices: number[], { sx, sy }: PatchData): void;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace Patch {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
    }
    interface Props extends XYGlyph.Props {
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface Patch extends Patch.Attrs {
}
export declare class Patch extends XYGlyph {
    properties: Patch.Props;
    constructor(attrs?: Partial<Patch.Attrs>);
    static initClass(): void;
}
