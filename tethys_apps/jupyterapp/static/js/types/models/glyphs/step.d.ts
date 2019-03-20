import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { StepMode } from "core/enums";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
export interface StepData extends XYGlyphData {
}
export interface StepView extends StepData {
}
export declare class StepView extends XYGlyphView {
    model: Step;
    visuals: Step.Visuals;
    protected _render(ctx: Context2d, indices: number[], { sx, sy }: StepData): void;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace Step {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        mode: StepMode;
    }
    interface Props extends XYGlyph.Props {
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
    }
}
export interface Step extends Step.Attrs {
}
export declare class Step extends XYGlyph {
    properties: Step.Props;
    constructor(attrs?: Partial<Step.Attrs>);
    static initClass(): void;
}
