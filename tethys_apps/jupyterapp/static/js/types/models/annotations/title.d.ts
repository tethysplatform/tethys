import { TextAnnotation, TextAnnotationView } from "./text_annotation";
import { FontSizeSpec, ColorSpec, NumberSpec } from "core/vectorization";
import { Color } from "core/types";
import { LineJoin, LineCap } from "core/enums";
import { FontStyle, VerticalAlign, TextAlign, TextBaseline } from "core/enums";
export declare class TitleView extends TextAnnotationView {
    model: Title;
    visuals: Title.Visuals;
    initialize(options: any): void;
    protected _get_location(): [number, number];
    render(): void;
    protected _get_size(): number;
}
export declare namespace Title {
    interface BorderLine {
        border_line_color: Color;
        border_line_width: number;
        border_line_alpha: number;
        border_line_join: LineJoin;
        border_line_cap: LineCap;
        border_line_dash: number[];
        border_line_dash_offset: number;
    }
    interface BackgroundFill {
        background_fill_color: Color;
        background_fill_alpha: number;
    }
    interface Mixins extends BorderLine, BackgroundFill {
    }
    interface Attrs extends TextAnnotation.Attrs, Mixins {
        text: string;
        text_font: string;
        text_font_size: FontSizeSpec;
        text_font_style: FontStyle;
        text_color: ColorSpec;
        text_alpha: NumberSpec;
        vertical_align: VerticalAlign;
        align: TextAlign;
        offset: number;
        text_align: TextAlign;
        text_baseline: TextBaseline;
    }
    interface Props extends TextAnnotation.Props {
    }
    type Visuals = TextAnnotation.Visuals;
}
export interface Title extends Title.Attrs {
}
export declare class Title extends TextAnnotation {
    properties: Title.Props;
    constructor(attrs?: Partial<Title.Attrs>);
    static initClass(): void;
}
