import { CenterRotatable, CenterRotatableView, CenterRotatableData } from "./center_rotatable";
import { PointGeometry } from "core/geometry";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { IBBox } from "core/util/bbox";
import { Rect } from "core/util/spatial";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
export interface EllipseOvalData extends CenterRotatableData {
}
export interface EllipseOvalView extends EllipseOvalData {
}
export declare abstract class EllipseOvalView extends CenterRotatableView {
    model: EllipseOval;
    visuals: EllipseOval.Visuals;
    protected _set_data(): void;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, sw, sh, _angle }: EllipseOvalData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, { x0, y0, x1, y1 }: IBBox, index: number): void;
    protected _bounds({ minX, maxX, minY, maxY }: Rect): Rect;
}
export declare namespace EllipseOval {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends CenterRotatable.Attrs, Mixins {
    }
    interface Props extends CenterRotatable.Props {
    }
    interface Visuals extends CenterRotatable.Visuals {
    }
}
export interface EllipseOval extends EllipseOval.Attrs {
}
export declare abstract class EllipseOval extends CenterRotatable {
    properties: EllipseOval.Props;
    constructor(attrs?: Partial<EllipseOval.Attrs>);
    static initClass(): void;
}
