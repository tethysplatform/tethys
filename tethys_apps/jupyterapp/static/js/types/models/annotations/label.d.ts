import { TextAnnotation, TextAnnotationView } from "./text_annotation";
import { TextMixinScalar } from "core/property_mixins";
import { Color } from "core/types";
import { LineJoin, LineCap } from "core/enums";
import { SpatialUnits, AngleUnits } from "core/enums";
export declare class LabelView extends TextAnnotationView {
    model: Label;
    visuals: Label.Visuals;
    initialize(options: any): void;
    protected _get_size(): number;
    render(): void;
}
export declare namespace Label {
    interface BorderLine {
        border_line_color: Color;
        border_line_width: number;
        border_line_alpha: number;
        border_line_join: LineJoin;
        border_line_cap: LineCap;
        border_line_dash: number[];
        border_line_dash_offset: number;
    }
    interface BackgorundFill {
        background_fill_color: Color;
        background_fill_alpha: number;
    }
    interface Mixins extends TextMixinScalar, BorderLine, BackgorundFill {
    }
    interface Attrs extends TextAnnotation.Attrs, Mixins {
        x: number;
        x_units: SpatialUnits;
        y: number;
        y_units: SpatialUnits;
        text: string;
        angle: number;
        angle_units: AngleUnits;
        x_offset: number;
        y_offset: number;
        x_range_name: string;
        y_range_name: string;
    }
    interface Props extends TextAnnotation.Props {
    }
    type Visuals = TextAnnotation.Visuals;
}
export interface Label extends Label.Attrs {
}
export declare class Label extends TextAnnotation {
    properties: Label.Props;
    constructor(attrs?: Partial<Label.Attrs>);
    static initClass(): void;
}
