import { Program, VertexBuffer } from "gloo2";
import { Arrayable } from "core/types";
import { Context2d } from "core/util/canvas";
import { GlyphView } from "../glyph";
export declare abstract class BaseGLGlyph {
    readonly gl: WebGLRenderingContext;
    readonly glyph: GlyphView;
    protected nvertices: number;
    protected size_changed: boolean;
    protected data_changed: boolean;
    protected visuals_changed: boolean;
    constructor(gl: WebGLRenderingContext, glyph: GlyphView);
    protected abstract init(): void;
    set_data_changed(n: number): void;
    set_visuals_changed(): void;
    render(_ctx: Context2d, indices: number[], mainglyph: GlyphView): boolean;
    abstract draw(indices: number[], mainglyph: any, trans: Transform): void;
}
export declare type Transform = {
    pixel_ratio: number;
    width: number;
    height: number;
    dx: number;
    dy: number;
    sx: number;
    sy: number;
};
export declare function line_width(width: number): number;
export declare function fill_array_with_float(n: number, val: number): Float32Array;
export declare function fill_array_with_vec(n: number, m: number, val: Arrayable<number>): Float32Array;
export declare function visual_prop_is_singular(visual: any, propname: string): boolean;
export declare function attach_float(prog: Program, vbo: VertexBuffer & {
    used?: boolean;
}, att_name: string, n: number, visual: any, name: string): void;
export declare function attach_color(prog: Program, vbo: VertexBuffer & {
    used?: boolean;
}, att_name: string, n: number, visual: any, prefix: string): void;
