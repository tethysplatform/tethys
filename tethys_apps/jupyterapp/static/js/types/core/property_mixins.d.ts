import { Color } from "./types";
import { Scalar, NumberSpec, StringSpec, ColorSpec } from "core/vectorization";
import { LineJoin, LineCap, FontStyle, TextAlign, TextBaseline } from "core/enums";
export interface LineMixinScalar {
    line_color: Scalar<Color>;
    line_width: Scalar<number>;
    line_alpha: Scalar<number>;
    line_join: Scalar<LineJoin>;
    line_cap: Scalar<LineCap>;
    line_dash: Scalar<number[]>;
    line_dash_offset: Scalar<number>;
}
export interface FillMixinScalar {
    fill_color: Scalar<Color>;
    fill_alpha: Scalar<number>;
}
export interface TextMixinScalar {
    text_font: Scalar<string>;
    text_font_size: Scalar<string>;
    text_font_style: Scalar<FontStyle>;
    text_color: Scalar<Color>;
    text_alpha: Scalar<number>;
    text_align: Scalar<TextAlign>;
    text_baseline: Scalar<TextBaseline>;
    text_line_height: Scalar<number>;
}
export interface LineMixinVector {
    line_color: ColorSpec;
    line_width: NumberSpec;
    line_alpha: NumberSpec;
    line_join: Scalar<LineJoin>;
    line_cap: Scalar<LineCap>;
    line_dash: Scalar<number[]>;
    line_dash_offset: Scalar<number>;
}
export interface FillMixinVector {
    fill_color: ColorSpec;
    fill_alpha: NumberSpec;
}
export interface TextMixinVector {
    text_font: Scalar<string>;
    text_font_size: StringSpec;
    text_font_style: Scalar<FontStyle>;
    text_color: ColorSpec;
    text_alpha: NumberSpec;
    text_align: Scalar<TextAlign>;
    text_baseline: Scalar<TextBaseline>;
    text_line_height: Scalar<number>;
}
export declare const line: (prefix?: string) => {
    [key: string]: any;
};
export declare const fill: (prefix?: string) => {
    [key: string]: any;
};
export declare const text: (prefix?: string) => {
    [key: string]: any;
};
export declare function create(configs: string[]): {
    [key: string]: any;
};
