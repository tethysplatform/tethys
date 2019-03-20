import { Glyph, GlyphView, GlyphData } from "./glyph";
import { PointGeometry, RectGeometry, SpanGeometry } from "core/geometry";
import * as p from "core/properties";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Arrayable } from "core/types";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { SpatialIndex } from "core/util/spatial";
import { NumberSpec } from "core/vectorization";
import { Line, Fill } from "core/visuals";
import { Selection } from "../selections/selection";
export interface HexTileData extends GlyphData {
    _q: Arrayable<number>;
    _r: Arrayable<number>;
    _x: Arrayable<number>;
    _y: Arrayable<number>;
    _scale: Arrayable<number>;
    sx: Arrayable<number>;
    sy: Arrayable<number>;
    svx: number[];
    svy: number[];
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
    ssize: number;
}
export interface HexTileView extends HexTileData {
}
export declare class HexTileView extends GlyphView {
    model: HexTile;
    visuals: HexTile.Visuals;
    scenterx(i: number): number;
    scentery(i: number): number;
    protected _set_data(): void;
    protected _index_data(): SpatialIndex;
    map_data(): void;
    protected _get_unscaled_vertices(): [number[], number[]];
    protected _render(ctx: Context2d, indices: number[], { sx, sy, svx, svy, _scale }: HexTileData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _hit_span(geometry: SpanGeometry): Selection;
    protected _hit_rect(geometry: RectGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
}
export declare namespace HexTile {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends Glyph.Attrs {
        size: number;
        aspect_scale: number;
        scale: NumberSpec;
        orientation: "pointytop" | "flattop";
    }
    interface Props extends Glyph.Props {
        size: p.Number;
        aspect_scale: p.Number;
        scale: p.NumberSpec;
        orientation: p.Property<"pointytop" | "flattop">;
    }
    interface Visuals extends Glyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface HexTile extends HexTile.Attrs {
}
export declare class HexTile extends Glyph {
    properties: HexTile.Props;
    constructor(attrs?: Partial<HexTile.Attrs>);
    static initClass(): void;
}
