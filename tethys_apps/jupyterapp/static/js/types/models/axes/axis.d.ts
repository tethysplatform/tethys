import { GuideRenderer, GuideRendererView } from "../renderers/guide_renderer";
import { Ticker } from "../tickers/ticker";
import { TickFormatter } from "../formatters/tick_formatter";
import { Range } from "../ranges/range";
import { Color } from "core/types";
import { FontStyle, TextAlign, TextBaseline, LineJoin, LineCap } from "core/enums";
import { Side, TickLabelOrientation, SpatialUnits } from "core/enums";
import { Text, Line } from "core/visuals";
import { SidePanel, Orient } from "core/layout/side_panel";
import { Context2d } from "core/util/canvas";
import { Factor } from "models/ranges/factor_range";
export interface Extents {
    tick: number;
    tick_label: number[];
    axis_label: number;
}
export declare type Coords = [number[], number[]];
export interface TickCoords {
    major: Coords;
    minor: Coords;
}
export declare class AxisView extends GuideRendererView {
    model: Axis;
    visuals: Axis.Visuals;
    render(): void;
    protected _render?(ctx: Context2d, extents: Extents, tick_coords: TickCoords): void;
    connect_signals(): void;
    get_size(): number;
    protected _get_size(): number;
    readonly needs_clip: boolean;
    protected _draw_rule(ctx: Context2d, _extents: Extents): void;
    protected _draw_major_ticks(ctx: Context2d, _extents: Extents, tick_coords: TickCoords): void;
    protected _draw_minor_ticks(ctx: Context2d, _extents: Extents, tick_coords: TickCoords): void;
    protected _draw_major_labels(ctx: Context2d, extents: Extents, tick_coords: TickCoords): void;
    protected _draw_axis_label(ctx: Context2d, extents: Extents, _tick_coords: TickCoords): void;
    protected _draw_ticks(ctx: Context2d, coords: Coords, tin: number, tout: number, visuals: Line): void;
    protected _draw_oriented_labels(ctx: Context2d, labels: string[], coords: Coords, orient: Orient | number, _side: Side, standoff: number, visuals: Text, units?: SpatialUnits): void;
    _axis_label_extent(): number;
    _tick_extent(): number;
    _tick_label_extent(): number;
    protected _tick_label_extents(): number[];
    protected _oriented_labels_extent(labels: string[], orient: Orient | number, side: Side, standoff: number, visuals: Text): number;
}
export declare namespace Axis {
    interface AxisLine {
        axis_line_color: Color;
        axis_line_width: number;
        axis_line_alpha: number;
        axis_line_join: LineJoin;
        axis_line_cap: LineCap;
        axis_line_dash: number[];
        axis_line_dash_offset: number;
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
    interface AxisLabelText {
        axis_label_text_font: string;
        axis_label_text_font_size: string;
        axis_label_text_font_style: FontStyle;
        axis_label_text_color: Color;
        axis_label_text_alpha: number;
        axis_label_text_align: TextAlign;
        axis_label_text_baseline: TextBaseline;
        axis_label_text_line_height: number;
    }
    interface Mixins extends AxisLine, MajorTickLine, MinorTickLine, MajorLabelText, AxisLabelText {
    }
    interface Attrs extends GuideRenderer.Attrs, Mixins {
        bounds: [number, number] | "auto";
        ticker: Ticker<any>;
        formatter: TickFormatter;
        x_range_name: string;
        y_range_name: string;
        axis_label: string | null;
        axis_label_standoff: number;
        major_label_standoff: number;
        major_label_orientation: TickLabelOrientation | number;
        major_label_overrides: {
            [key: string]: string;
        };
        major_tick_in: number;
        major_tick_out: number;
        minor_tick_in: number;
        minor_tick_out: number;
        fixed_location: number | Factor | null;
    }
    interface Props extends GuideRenderer.Props {
    }
    type Visuals = GuideRenderer.Visuals & {
        axis_line: Line;
        major_tick_line: Line;
        minor_tick_line: Line;
        major_label_text: Text;
        axis_label_text: Text;
    };
}
export interface Axis extends Axis.Attrs {
    panel: SidePanel;
}
export declare class Axis extends GuideRenderer {
    properties: Axis.Props;
    constructor(attrs?: Partial<Axis.Attrs>);
    static initClass(): void;
    add_panel(side: Side): void;
    readonly normals: [number, number];
    readonly dimension: 0 | 1;
    compute_labels(ticks: number[]): string[];
    readonly offsets: [number, number];
    readonly ranges: [Range, Range];
    readonly computed_bounds: [number, number];
    readonly rule_coords: Coords;
    readonly tick_coords: TickCoords;
    readonly loc: number;
}
