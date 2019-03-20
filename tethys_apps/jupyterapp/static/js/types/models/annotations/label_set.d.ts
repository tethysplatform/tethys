import { TextAnnotation, TextAnnotationView } from "./text_annotation";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { NumberSpec, AngleSpec, StringSpec, ColorSpec } from "core/vectorization";
import { TextMixinVector } from "core/property_mixins";
import { LineJoin, LineCap } from "core/enums";
import { SpatialUnits } from "core/enums";
import { Arrayable } from "core/types";
import { Context2d } from "core/util/canvas";
export declare class LabelSetView extends TextAnnotationView {
    model: LabelSet;
    visuals: LabelSet.Visuals;
    protected _x: Arrayable<number>;
    protected _y: Arrayable<number>;
    protected _text: Arrayable<string>;
    protected _angle: Arrayable<number>;
    protected _x_offset: Arrayable<number>;
    protected _y_offset: Arrayable<number>;
    initialize(options: any): void;
    connect_signals(): void;
    set_data(source: ColumnarDataSource): void;
    protected _map_data(): [Arrayable<number>, Arrayable<number>];
    render(): void;
    protected _get_size(): number;
    protected _v_canvas_text(ctx: Context2d, i: number, text: string, sx: number, sy: number, angle: number): void;
    protected _v_css_text(ctx: Context2d, i: number, text: string, sx: number, sy: number, angle: number): void;
}
export declare namespace LabelSet {
    interface BorderLine {
        border_line_color: ColorSpec;
        border_line_width: NumberSpec;
        border_line_alpha: NumberSpec;
        border_line_join: LineJoin;
        border_line_cap: LineCap;
        border_line_dash: number[];
        border_line_dash_offset: number;
    }
    interface BackgroundFill {
        background_fill_color: ColorSpec;
        background_fill_alpha: NumberSpec;
    }
    interface Mixins extends TextMixinVector, BorderLine, BackgroundFill {
    }
    interface Attrs extends TextAnnotation.Attrs, Mixins {
        x: NumberSpec;
        y: NumberSpec;
        x_units: SpatialUnits;
        y_units: SpatialUnits;
        text: StringSpec;
        angle: AngleSpec;
        x_offset: NumberSpec;
        y_offset: NumberSpec;
        source: ColumnarDataSource;
        x_range_name: string;
        y_range_name: string;
    }
    interface Props extends TextAnnotation.Props {
    }
    type Visuals = TextAnnotation.Visuals;
}
export interface LabelSet extends LabelSet.Attrs {
}
export declare class LabelSet extends TextAnnotation {
    properties: LabelSet.Props;
    constructor(attrs?: Partial<LabelSet.Attrs>);
    static initClass(): void;
}
