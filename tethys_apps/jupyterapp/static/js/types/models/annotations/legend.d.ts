import { Annotation, AnnotationView } from "./annotation";
import { LegendItem } from "./legend_item";
import { Color } from "core/types";
import { Line, Fill, Text } from "core/visuals";
import { FontStyle, TextAlign, TextBaseline, LineJoin, LineCap } from "core/enums";
import { Orientation, LegendLocation, LegendClickPolicy } from "core/enums";
import { Signal0 } from "core/signaling";
import { BBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
export declare type LegendBBox = {
    x: number;
    y: number;
    width: number;
    height: number;
};
export declare class LegendView extends AnnotationView {
    model: Legend;
    visuals: Legend.Visuals;
    protected max_label_height: number;
    protected text_widths: {
        [key: string]: number;
    };
    cursor(_sx: number, _sy: number): string | null;
    readonly legend_padding: number;
    connect_signals(): void;
    compute_legend_bbox(): LegendBBox;
    interactive_bbox(): BBox;
    interactive_hit(sx: number, sy: number): boolean;
    on_hit(sx: number, sy: number): boolean;
    render(): void;
    protected _draw_legend_box(ctx: Context2d, bbox: LegendBBox): void;
    protected _draw_legend_items(ctx: Context2d, bbox: LegendBBox): void;
    protected _get_size(): number;
}
export declare namespace Legend {
    interface LabelText {
        label_text_font: string;
        label_text_font_size: string;
        label_text_font_style: FontStyle;
        label_text_color: Color;
        label_text_alpha: number;
        label_text_align: TextAlign;
        label_text_baseline: TextBaseline;
        label_text_line_height: number;
    }
    interface InactiveFill {
        inactive_fill_color: Color;
        inactive_fill_alpha: number;
    }
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
    interface Mixins extends LabelText, InactiveFill, BorderLine, BackgroundFill {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        orientation: Orientation;
        location: LegendLocation | [number, number];
        label_standoff: number;
        glyph_height: number;
        glyph_width: number;
        label_height: number;
        label_width: number;
        margin: number;
        padding: number;
        spacing: number;
        items: LegendItem[];
        click_policy: LegendClickPolicy;
    }
    interface Props extends Annotation.Props {
    }
    type Visuals = Annotation.Visuals & {
        label_text: Text;
        inactive_fill: Fill;
        border_line: Line;
        background_fill: Fill;
    };
}
export interface Legend extends Legend.Attrs {
}
export declare class Legend extends Annotation {
    properties: Legend.Props;
    item_change: Signal0<this>;
    constructor(attrs?: Partial<Legend.Attrs>);
    initialize(): void;
    static initClass(): void;
    get_legend_names(): string[];
}
