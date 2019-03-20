import { Marker, MarkerView, MarkerData } from "./marker";
import { Arrayable } from "core/types";
import { Context2d } from "core/util/canvas";
import { IBBox } from "core/util/bbox";
export interface ScatterData extends MarkerData {
    _marker: Arrayable<string>;
}
export interface ScatterView extends ScatterData {
}
export declare class ScatterView extends MarkerView {
    model: Scatter;
    protected _render(ctx: Context2d, indices: number[], { sx, sy, _size, _angle, _marker }: ScatterData): void;
    draw_legend_for_index(ctx: Context2d, { x0, x1, y0, y1 }: IBBox, index: number): void;
}
export declare namespace Scatter {
    interface Attrs extends Marker.Attrs {
        marker: string;
    }
    interface Props extends Marker.Props {
    }
}
export interface Scatter extends Scatter.Attrs {
}
export declare abstract class Scatter extends Marker {
    properties: Scatter.Props;
    constructor(attrs?: Partial<Scatter.Attrs>);
    static initClass(): void;
}
