import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { DistanceSpec, NumberSpec } from "core/vectorization";
import { Arrayable, TypedArray } from "core/types";
import * as p from "core/properties";
import { Context2d } from "core/util/canvas";
import { Rect } from "core/util/spatial";
export interface ImageRGBAData extends XYGlyphData {
    image_data: Arrayable<HTMLCanvasElement>;
    _image: Arrayable<TypedArray | number[][]>;
    _dw: Arrayable<number>;
    _dh: Arrayable<number>;
    _image_shape?: Arrayable<[number, number]>;
    sw: Arrayable<number>;
    sh: Arrayable<number>;
    max_dw: number;
    max_dh: number;
}
export interface ImageRGBAView extends ImageRGBAData {
}
export declare class ImageRGBAView extends XYGlyphView {
    model: ImageRGBA;
    visuals: ImageRGBA.Visuals;
    protected _width: Arrayable<number>;
    protected _height: Arrayable<number>;
    initialize(options: any): void;
    protected _set_data(indices: number[] | null): void;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { image_data, sx, sy, sw, sh }: ImageRGBAData): void;
    bounds(): Rect;
}
export declare namespace ImageRGBA {
    interface Attrs extends XYGlyph.Attrs {
        image: NumberSpec;
        dw: DistanceSpec;
        dh: DistanceSpec;
        global_alpha: number;
        dilate: boolean;
    }
    interface Props extends XYGlyph.Props {
        image: p.NumberSpec;
        dw: p.DistanceSpec;
        dh: p.DistanceSpec;
        global_alpha: p.Property<number>;
        dilate: p.Property<boolean>;
    }
    interface Visuals extends XYGlyph.Visuals {
    }
}
export interface ImageRGBA extends ImageRGBA.Attrs {
}
export declare class ImageRGBA extends XYGlyph {
    properties: ImageRGBA.Props;
    constructor(attrs?: Partial<ImageRGBA.Attrs>);
    static initClass(): void;
}
