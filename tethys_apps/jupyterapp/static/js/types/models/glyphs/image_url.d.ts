import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { DistanceSpec, AngleSpec, StringSpec } from "core/vectorization";
import { Arrayable } from "core/types";
import { Anchor } from "core/enums";
import * as p from "core/properties";
import { Context2d } from "core/util/canvas";
import { Rect, SpatialIndex } from "core/util/spatial";
export declare type CanvasImage = HTMLImageElement;
export declare const CanvasImage: new (width?: number | undefined, height?: number | undefined) => HTMLImageElement;
export interface ImageURLData extends XYGlyphData {
    _url: Arrayable<string>;
    _angle: Arrayable<number>;
    _w: Arrayable<number>;
    _h: Arrayable<number>;
    _bounds_rect: Rect;
    sx: Arrayable<number>;
    sy: Arrayable<number>;
    sw: Arrayable<number>;
    sh: Arrayable<number>;
    max_w: number;
    max_h: number;
    image: Arrayable<CanvasImage | null>;
}
export interface ImageURLView extends ImageURLData {
}
export declare class ImageURLView extends XYGlyphView {
    model: ImageURL;
    visuals: ImageURL.Visuals;
    protected retries: Arrayable<number>;
    protected _images_rendered: boolean;
    initialize(options: any): void;
    protected _index_data(): SpatialIndex;
    protected _set_data(): void;
    has_finished(): boolean;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { image, sx, sy, sw, sh, _angle }: ImageURLData): void;
    protected _final_sx_sy(anchor: Anchor, sx: number, sy: number, sw: number, sh: number): [number, number];
    protected _render_image(ctx: Context2d, i: number, image: CanvasImage, sx: Arrayable<number>, sy: Arrayable<number>, sw: Arrayable<number>, sh: Arrayable<number>, angle: Arrayable<number>): void;
    bounds(): Rect;
}
export declare namespace ImageURL {
    interface Attrs extends XYGlyph.Attrs {
        url: StringSpec;
        anchor: Anchor;
        global_alpha: number;
        angle: AngleSpec;
        w: DistanceSpec;
        h: DistanceSpec;
        dilate: boolean;
        retry_attempts: number;
        retry_timeout: number;
    }
    interface Props extends XYGlyph.Props {
        url: p.StringSpec;
        anchor: p.Property<Anchor>;
        global_alpha: p.Property<number>;
        angle: p.AngleSpec;
        w: p.DistanceSpec;
        h: p.DistanceSpec;
        dilate: p.Property<boolean>;
        retry_attempts: p.Property<number>;
        retry_timeout: p.Property<number>;
    }
    interface Visuals extends XYGlyph.Visuals {
    }
}
export interface ImageURL extends ImageURL.Attrs {
}
export declare class ImageURL extends XYGlyph {
    properties: ImageURL.Props;
    constructor(attrs?: Partial<ImageURL.Attrs>);
    static initClass(): void;
}
