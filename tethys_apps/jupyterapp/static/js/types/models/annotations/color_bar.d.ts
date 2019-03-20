import { Annotation, AnnotationView } from "./annotation";
import { ContinuousTicker } from "../tickers/continuous_ticker";
import { TickFormatter } from "../formatters/tick_formatter";
import { ContinuousColorMapper } from "../mappers/continuous_color_mapper";
import { Scale } from "../scales/scale";
import { Arrayable, Color } from "core/types";
import { Line, Fill, Text } from "core/visuals";
import { FontStyle, TextAlign, TextBaseline, LineJoin, LineCap } from "core/enums";
import { LegendLocation, Orientation } from "core/enums";
import { Context2d } from "core/util/canvas";
export declare type Coords = [Arrayable<number>, Arrayable<number>];
export declare type TickInfo = {
    coords: {
        major: Coords;
        minor: Coords;
    };
    labels: {
        major: string[];
    };
};
export declare class ColorBarView extends AnnotationView {
    model: ColorBar;
    visuals: ColorBar.Visuals;
    protected image: HTMLCanvasElement;
    initialize(options: any): void;
    connect_signals(): void;
    protected _get_size(): number;
    protected _set_canvas_image(): void;
    compute_legend_dimensions(): {
        width: number;
        height: number;
    };
    compute_legend_location(): {
        sx: number;
        sy: number;
    };
    render(): void;
    protected _draw_bbox(ctx: Context2d): void;
    protected _draw_image(ctx: Context2d): void;
    protected _draw_major_ticks(ctx: Context2d, tick_info: TickInfo): void;
    protected _draw_minor_ticks(ctx: Context2d, tick_info: TickInfo): void;
    protected _draw_major_labels(ctx: Context2d, tick_info: TickInfo): void;
    protected _draw_title(ctx: Context2d): void;
    protected _get_label_extent(): number;
    protected _get_image_offset(): {
        x: number;
        y: number;
    };
}
export declare namespace ColorBar {
    interface MajorLabelText {
        major_label_text_font: string;
        major_label_text_font_size: string;
        major_label_text_font_style: FontStyle;
        major_label_text_color: Color;
        major_label_text_alpha: number;
        major_label_text_align: TextAlign;
        major_label_text_baseline: TextBaseline;
        major_label_text_line_height: number;
    }
    interface TitleText {
        title_text_font: string;
        title_text_font_size: string;
        title_text_font_style: FontStyle;
        title_text_color: Color;
        title_text_alpha: number;
        title_text_align: TextAlign;
        title_text_baseline: TextBaseline;
        title_text_line_height: number;
    }
    interface MajorTickLine {
        major_tick_line_color: Color;
        major_tick_line_width: number;
        major_tick_line_alpha: number;
        major_tick_line_join: LineJoin;
        major_tick_line_cap: LineCap;
        major_tick_line_dash: number[];
        major_tick_line_dash_offset: number;
    }
    interface MinorTickLine {
        minor_tick_line_color: Color;
        minor_tick_line_width: number;
        minor_tick_line_alpha: number;
        minor_tick_line_join: LineJoin;
        minor_tick_line_cap: LineCap;
        minor_tick_line_dash: number[];
        minor_tick_line_dash_offset: number;
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
    interface BarLine {
        bar_line_color: Color;
        bar_line_width: number;
        bar_line_alpha: number;
        bar_line_join: LineJoin;
        bar_line_cap: LineCap;
        bar_line_dash: number[];
        bar_line_dash_offset: number;
    }
    interface BackgroundFill {
        background_fill_color: Color;
        background_fill_alpha: number;
    }
    interface Mixins extends MajorLabelText, TitleText, MajorTickLine, MinorTickLine, BorderLine, BarLine, BackgroundFill {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        location: LegendLocation | [number, number];
        orientation: Orientation;
        title: string;
        title_standoff: number;
        width: number | "auto";
        height: number | "auto";
        scale_alpha: number;
        ticker: ContinuousTicker;
        formatter: TickFormatter;
        major_label_overrides: {
            [key: string]: string;
        };
        color_mapper: ContinuousColorMapper;
        label_standoff: number;
        margin: number;
        padding: number;
        major_tick_in: number;
        major_tick_out: number;
        minor_tick_in: number;
        minor_tick_out: number;
    }
    interface Props extends Annotation.Props {
    }
    type Visuals = Annotation.Visuals & {
        major_label_text: Text;
        title_text: Text;
        major_tick_line: Line;
        minor_tick_line: Line;
        border_line: Line;
        bar_line: Line;
        background_fill: Fill;
    };
}
export interface ColorBar extends ColorBar.Attrs {
}
export declare class ColorBar extends Annotation {
    properties: ColorBar.Props;
    constructor(attrs?: Partial<ColorBar.Attrs>);
    static initClass(): void;
    _normals(): [number, number];
    _title_extent(): number;
    _tick_extent(): number;
    _computed_image_dimensions(): {
        height: number;
        width: number;
    };
    protected _tick_coordinate_scale(scale_length: number): Scale;
    protected _format_major_labels(initial_labels: number[], major_ticks: Arrayable<number>): string[];
    tick_info(): TickInfo;
}
