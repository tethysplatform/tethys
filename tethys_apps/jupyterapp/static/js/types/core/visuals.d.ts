import * as p from "./properties";
import { Context2d } from "./util/canvas";
import { HasProps } from "./has_props";
import { ColumnarDataSource } from "models/sources/columnar_data_source";
export declare abstract class ContextProperties {
    readonly obj: HasProps;
    readonly prefix: string;
    attrs: string[];
    do_attr: string;
    readonly cache: {
        [key: string]: any;
    };
    readonly doit: boolean;
    all_indices: number[];
    constructor(obj: HasProps, prefix?: string);
    warm_cache(source?: ColumnarDataSource): void;
    cache_select(attr: string, i: number): any;
    set_vectorize(ctx: Context2d, i: number): void;
    protected abstract _set_vectorize(ctx: Context2d, i: number): void;
}
export declare class Line extends ContextProperties {
    readonly line_color: p.ColorSpec;
    readonly line_width: p.NumberSpec;
    readonly line_alpha: p.NumberSpec;
    readonly line_join: p.LineJoin;
    readonly line_cap: p.LineCap;
    readonly line_dash: p.Array;
    readonly line_dash_offset: p.Number;
    set_value(ctx: Context2d): void;
    protected _set_vectorize(ctx: Context2d, i: number): void;
    color_value(): string;
}
export declare class Fill extends ContextProperties {
    readonly fill_color: p.ColorSpec;
    readonly fill_alpha: p.NumberSpec;
    set_value(ctx: Context2d): void;
    protected _set_vectorize(ctx: Context2d, i: number): void;
    color_value(): string;
}
export declare class Text extends ContextProperties {
    readonly text_font: p.Font;
    readonly text_font_size: p.FontSizeSpec;
    readonly text_font_style: p.FontStyle;
    readonly text_color: p.ColorSpec;
    readonly text_alpha: p.NumberSpec;
    readonly text_align: p.TextAlign;
    readonly text_baseline: p.TextBaseline;
    readonly text_line_height: p.Number;
    cache_select(name: string, i: number): any;
    font_value(): string;
    color_value(): string;
    set_value(ctx: Context2d): void;
    protected _set_vectorize(ctx: Context2d, i: number): void;
}
export declare class Visuals {
    constructor(model: HasProps);
    warm_cache(source?: ColumnarDataSource): void;
    set_all_indices(all_indices: number[]): void;
}
