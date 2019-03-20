import { Program, VertexBuffer, IndexBuffer } from "gloo2";
import { BaseGLGlyph, Transform } from "./base";
import { MarkerView } from "../../markers/marker";
import { CircleView } from "../circle";
import { Class } from "core/class";
export declare abstract class MarkerGLGlyph extends BaseGLGlyph {
    readonly glyph: MarkerView | CircleView;
    protected abstract readonly _marker_code: string;
    protected prog: Program;
    protected vbo_x: VertexBuffer;
    protected vbo_y: VertexBuffer;
    protected vbo_s: VertexBuffer;
    protected vbo_a: VertexBuffer;
    protected vbo_linewidth: VertexBuffer & {
        used?: boolean;
    };
    protected vbo_fg_color: VertexBuffer & {
        used?: boolean;
    };
    protected vbo_bg_color: VertexBuffer & {
        used?: boolean;
    };
    protected index_buffer: IndexBuffer;
    protected last_trans: Transform;
    protected _baked_offset: [number, number];
    protected init(): void;
    draw(indices: number[], mainGlyph: MarkerView | CircleView, trans: Transform): void;
    protected _set_data(nvertices: number): void;
    protected _set_visuals(nvertices: number): void;
}
export declare const CircleGLGlyph: Class<MarkerGLGlyph>;
export declare const SquareGLGlyph: Class<MarkerGLGlyph>;
export declare const DiamondGLGlyph: Class<MarkerGLGlyph>;
export declare const TriangleGLGlyph: Class<MarkerGLGlyph>;
export declare const InvertedTriangleGLGlyph: Class<MarkerGLGlyph>;
export declare const HexGLGlyph: Class<MarkerGLGlyph>;
export declare const CrossGLGlyph: Class<MarkerGLGlyph>;
export declare const CircleCrossGLGlyph: Class<MarkerGLGlyph>;
export declare const SquareCrossGLGlyph: Class<MarkerGLGlyph>;
export declare const DiamondCrossGLGlyph: Class<MarkerGLGlyph>;
export declare const XGLGlyph: Class<MarkerGLGlyph>;
export declare const CircleXGLGlyph: Class<MarkerGLGlyph>;
export declare const SquareXGLGlyph: Class<MarkerGLGlyph>;
export declare const AsteriskGLGlyph: Class<MarkerGLGlyph>;
