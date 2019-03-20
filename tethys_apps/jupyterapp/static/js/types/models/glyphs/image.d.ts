import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { DistanceSpec, NumberSpec } from "core/vectorization";
import { ColorMapper } from "../mappers/color_mapper";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import { Context2d } from "core/util/canvas";
import { Rect } from "core/util/spatial";
import { SpatialIndex } from "core/util/spatial";
import { Selection } from "../selections/selection";
import { PointGeometry } from "core/geometry";
export interface _ImageData extends XYGlyphData {
    image_data: Arrayable<HTMLCanvasElement>;
    _image: Arrayable<Arrayable<number> | number[][]>;
    _dw: Arrayable<number>;
    _dh: Arrayable<number>;
    _image_shape?: Arrayable<[number, number]>;
    sw: Arrayable<number>;
    sh: Arrayable<number>;
    max_dw: number;
    max_dh: number;
}
export interface ImageView extends _ImageData {
}
export interface ImageIndex {
    index: number;
    dim1: number;
    dim2: number;
    flat_index: number;
}
export declare class ImageView extends XYGlyphView {
    model: Image;
    visuals: Image.Visuals;
    protected _width: Arrayable<number>;
    protected _height: Arrayable<number>;
    initialize(options: any): void;
    protected _update_image(): void;
    _index_data(): SpatialIndex;
    _lrtb(i: number): [number, number, number, number];
    _image_index(index: number, x: number, y: number): ImageIndex;
    _hit_point(geometry: PointGeometry): Selection;
    protected _set_data(): void;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { image_data, sx, sy, sw, sh }: _ImageData): void;
    bounds(): Rect;
}
export declare namespace Image {
    interface Attrs extends XYGlyph.Attrs {
        image: NumberSpec;
        dw: DistanceSpec;
        dh: DistanceSpec;
        global_alpha: number;
        dilate: boolean;
        color_mapper: ColorMapper;
    }
    interface Props extends XYGlyph.Props {
        image: p.NumberSpec;
        dw: p.DistanceSpec;
        dh: p.DistanceSpec;
        global_alpha: p.Property<number>;
        dilate: p.Property<boolean>;
        color_mapper: p.Property<ColorMapper>;
    }
    interface Visuals extends XYGlyph.Visuals {
    }
}
export interface Image extends Image.Attrs {
}
export declare class Image extends XYGlyph {
    properties: Image.Props;
    constructor(attrs?: Partial<Image.Attrs>);
    static initClass(): void;
}
