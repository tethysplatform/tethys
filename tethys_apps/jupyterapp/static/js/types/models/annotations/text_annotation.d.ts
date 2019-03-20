import { Annotation, AnnotationView } from "./annotation";
import { Text, Line, Fill } from "core/visuals";
import { RenderMode } from "core/enums";
import { Context2d } from "core/util/canvas";
export declare abstract class TextAnnotationView extends AnnotationView {
    model: TextAnnotation;
    visuals: TextAnnotation.Visuals;
    initialize(options: any): void;
    connect_signals(): void;
    protected _calculate_text_dimensions(ctx: Context2d, text: string): [number, number];
    protected _calculate_bounding_box_dimensions(ctx: Context2d, text: string): [number, number, number, number];
    abstract render(): void;
    protected _canvas_text(ctx: Context2d, text: string, sx: number, sy: number, angle: number): void;
    protected _css_text(ctx: Context2d, text: string, sx: number, sy: number, angle: number): void;
}
export declare namespace TextAnnotation {
    interface Attrs extends Annotation.Attrs {
        render_mode: RenderMode;
    }
    interface Props extends Annotation.Props {
    }
    type Visuals = Annotation.Visuals & {
        text: Text;
        border_line: Line;
        background_fill: Fill;
    };
}
export interface TextAnnotation extends TextAnnotation.Attrs {
}
export declare abstract class TextAnnotation extends Annotation {
    properties: TextAnnotation.Props;
    constructor(attrs?: Partial<TextAnnotation.Attrs>);
    static initClass(): void;
}
