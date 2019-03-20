import { GestureEvent } from "core/ui_events";
import { BoxAnnotation } from "../../annotations/box_annotation";
import { Range } from "../../ranges/range";
import { Range1d } from "../../ranges/range1d";
import { Scale } from '../../scales/scale';
import { GestureTool, GestureToolView } from "./gesture_tool";
export declare function is_near(pos: number, value: number | null, scale: Scale, tolerance: number): boolean;
export declare function is_inside(sx: number, sy: number, xscale: Scale, yscale: Scale, overlay: BoxAnnotation): boolean;
export declare function compute_value(value: number, scale: Scale, sdelta: number, range: Range): number;
export declare function update_range(range: Range1d, scale: Scale, delta: number, plot_range: Range): void;
export declare class RangeToolView extends GestureToolView {
    model: RangeTool;
    private last_dx;
    private last_dy;
    private side;
    initialize(options: any): void;
    connect_signals(): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(_ev: GestureEvent): void;
}
export declare namespace RangeTool {
    interface Attrs extends GestureTool.Attrs {
        x_range: Range1d | null;
        x_interaction: boolean;
        y_range: Range1d | null;
        y_interaction: boolean;
        overlay: BoxAnnotation;
    }
    interface Props extends GestureTool.Props {
    }
}
export interface RangeTool extends RangeTool.Attrs {
}
export declare class RangeTool extends GestureTool {
    properties: RangeTool.Props;
    constructor(attrs?: Partial<RangeTool.Attrs>);
    static initClass(): void;
    initialize(): void;
    update_overlay_from_ranges(): void;
    tool_name: string;
    icon: string;
    event_type: "pan";
    default_order: number;
}
