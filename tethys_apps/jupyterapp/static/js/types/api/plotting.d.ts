import * as models from "./models";
import { HasProps } from "../core/has_props";
import { Class } from "../core/class";
import { Location } from "../core/enums";
import { StringSpec } from "../core/vectorization";
import { Glyph, GlyphRenderer, Axis, Grid, Range, Scale, Tool, Plot, ColumnarDataSource } from "./models";
import { DOMView } from "../core/dom_view";
import { Legend } from "models/annotations/legend";
export { gridplot } from "./gridplot";
export declare type ToolName = "pan" | "xpan" | "ypan" | "xwheel_pan" | "ywheel_pan" | "wheel_zoom" | "xwheel_zoom" | "ywheel_zoom" | "zoom_in" | "xzoom_in" | "yzoom_in" | "zoom_out" | "xzoom_out" | "yzoom_out" | "click" | "tap" | "box_select" | "xbox_select" | "ybox_select" | "poly_select" | "lasso_select" | "box_zoom" | "xbox_zoom" | "ybox_zoom" | "crosshair" | "hover" | "save" | "undo" | "redo" | "reset" | "help";
export declare type AxisType = "auto" | "linear" | "datetime" | "log" | null;
export interface FigureAttrs {
    width?: number;
    height?: number;
    x_range?: Range | [number, number] | string[];
    y_range?: Range | [number, number] | string[];
    x_axis_type?: AxisType;
    y_axis_type?: AxisType;
    x_axis_label?: string;
    y_axis_label?: string;
    x_minor_ticks?: number | "auto";
    y_minor_ticks?: number | "auto";
    tools?: (Tool | ToolName)[] | string;
}
export declare class Figure extends Plot {
    readonly xgrid: Grid;
    readonly ygrid: Grid;
    readonly xaxis: Axis;
    readonly yaxis: Axis;
    protected _legend: Legend;
    constructor(attributes?: any);
    annular_wedge(...args: any[]): GlyphRenderer;
    annulus(...args: any[]): GlyphRenderer;
    arc(...args: any[]): GlyphRenderer;
    bezier(...args: any[]): GlyphRenderer;
    circle(...args: any[]): GlyphRenderer;
    ellipse(...args: any[]): GlyphRenderer;
    image(...args: any[]): GlyphRenderer;
    image_rgba(...args: any[]): GlyphRenderer;
    image_url(...args: any[]): GlyphRenderer;
    line(...args: any[]): GlyphRenderer;
    multi_line(...args: any[]): GlyphRenderer;
    oval(...args: any[]): GlyphRenderer;
    patch(...args: any[]): GlyphRenderer;
    patches(...args: any[]): GlyphRenderer;
    quad(...args: any[]): GlyphRenderer;
    quadratic(...args: any[]): GlyphRenderer;
    ray(...args: any[]): GlyphRenderer;
    rect(...args: any[]): GlyphRenderer;
    segment(...args: any[]): GlyphRenderer;
    text(...args: any[]): GlyphRenderer;
    wedge(...args: any[]): GlyphRenderer;
    asterisk(...args: any[]): GlyphRenderer;
    circle_cross(...args: any[]): GlyphRenderer;
    circle_x(...args: any[]): GlyphRenderer;
    cross(...args: any[]): GlyphRenderer;
    dash(...args: any[]): GlyphRenderer;
    diamond(...args: any[]): GlyphRenderer;
    diamond_cross(...args: any[]): GlyphRenderer;
    inverted_triangle(...args: any[]): GlyphRenderer;
    square(...args: any[]): GlyphRenderer;
    square_cross(...args: any[]): GlyphRenderer;
    square_x(...args: any[]): GlyphRenderer;
    triangle(...args: any[]): GlyphRenderer;
    x(...args: any[]): GlyphRenderer;
    _pop_colors_and_alpha(cls: Class<HasProps>, attrs: {
        [key: string]: any;
    }, prefix?: string, default_color?: string, default_alpha?: number): {
        [key: string]: any;
    };
    _find_uniq_name(data: {
        [key: string]: any[];
    }, name: string): string;
    _fixup_values(cls: Class<HasProps>, data: {
        [key: string]: any;
    }, attrs: {
        [key: string]: any;
    }): void;
    _glyph(cls: Class<Glyph>, params_string: string, args: any): GlyphRenderer;
    _marker(cls: Class<Glyph>, args: any): GlyphRenderer;
    static _get_range(range?: Range | [number, number] | string[]): Range;
    static _get_scale(range_input: Range, axis_type: AxisType): Scale;
    _process_axis_and_grid(axis_type: AxisType, axis_location: Location, minor_ticks: number | "auto" | undefined, axis_label: string, rng: Range, dim: 0 | 1): void;
    _get_axis_class(axis_type: AxisType, range: Range): Class<Axis> | null;
    _get_num_minor_ticks(axis_class: Class<Axis>, num_minor_ticks?: number | "auto"): number;
    _process_tools(tools: (Tool | string)[] | string): Tool[];
    _process_legend(legend: string | StringSpec | undefined, source: ColumnarDataSource): StringSpec | null;
    _update_legend(legend_item_label: StringSpec, glyph_renderer: GlyphRenderer): void;
}
export declare function figure(attributes?: any): Figure;
export declare const show: (obj: models.LayoutDOM | models.LayoutDOM[], target?: string | HTMLElement | undefined) => {
    [key: string]: DOMView;
};
export declare function color(r: number, g: number, b: number): string;
