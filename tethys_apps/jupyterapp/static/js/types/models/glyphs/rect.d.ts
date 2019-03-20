import { CenterRotatable, CenterRotatableView, CenterRotatableData } from "./center_rotatable";
import { PointGeometry, RectGeometry } from "core/geometry";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import * as spatial from "core/util/spatial";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
import { Scale } from "../scales/scale";
export interface RectData extends CenterRotatableData {
    sx0: Arrayable<number>;
    sy1: Arrayable<number>;
    ssemi_diag: Arrayable<number>;
}
export interface RectView extends RectData {
}
export declare class RectView extends CenterRotatableView {
    model: Rect;
    visuals: Rect.Visuals;
    protected _set_data(): void;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, sx0, sy1, sw, sh, _angle }: RectData): void;
    protected _hit_rect(geometry: RectGeometry): Selection;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _map_dist_corner_for_data_side_length(coord: Arrayable<number>, side_length: Arrayable<number>, scale: Scale): [Arrayable<number>, Arrayable<number>];
    protected _ddist(dim: 0 | 1, spts: Arrayable<number>, spans: Arrayable<number>): Arrayable<number>;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
    protected _bounds({ minX, maxX, minY, maxY }: spatial.Rect): spatial.Rect;
}
export declare namespace Rect {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends CenterRotatable.Attrs, Mixins {
        dilate: boolean;
    }
    interface Props extends CenterRotatable.Props {
        dilate: p.Property<boolean>;
    }
    interface Visuals extends CenterRotatable.Visuals {
    }
}
export interface Rect extends Rect.Attrs {
}
export declare class Rect extends CenterRotatable {
    properties: Rect.Props;
    constructor(attrs?: Partial<Rect.Attrs>);
    static initClass(): void;
}
