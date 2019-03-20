import { Scale } from "../scales/scale";
import { Range } from "../ranges/range";
import { Range1d } from "../ranges/range1d";
import { LayoutCanvas } from "core/layout/layout_canvas";
import { Variable } from "core/layout/solver";
import { Arrayable } from "core/types";
export declare type Ranges = {
    [key: string]: Range;
};
export declare type Scales = {
    [key: string]: Scale;
};
export declare namespace CartesianFrame {
    interface Attrs extends LayoutCanvas.Attrs {
        extra_x_ranges: Ranges;
        extra_y_ranges: Ranges;
        x_range: Range;
        y_range: Range;
        x_scale: Scale;
        y_scale: Scale;
    }
    interface Props extends LayoutCanvas.Props {
    }
}
export interface CartesianFrame extends CartesianFrame.Attrs {
}
export declare class CartesianFrame extends LayoutCanvas {
    constructor(attrs?: Partial<CartesianFrame.Attrs>);
    static initClass(): void;
    protected _h_target: Range1d;
    protected _v_target: Range1d;
    protected _x_ranges: Ranges;
    protected _y_ranges: Ranges;
    protected _xscales: Scales;
    protected _yscales: Scales;
    initialize(): void;
    connect_signals(): void;
    readonly panel: LayoutCanvas;
    get_editables(): Variable[];
    map_to_screen(x: Arrayable<number>, y: Arrayable<number>, x_name?: string, y_name?: string): [Arrayable<number>, Arrayable<number>];
    protected _get_ranges(range: Range, extra_ranges?: Ranges): Ranges;
    protected _get_scales(scale: Scale, ranges: Ranges, frame_range: Range): Scales;
    protected _configure_frame_ranges(): void;
    protected _configure_scales(): void;
    update_scales(): void;
    readonly x_ranges: Ranges;
    readonly y_ranges: Ranges;
    readonly xscales: Scales;
    readonly yscales: Scales;
}
