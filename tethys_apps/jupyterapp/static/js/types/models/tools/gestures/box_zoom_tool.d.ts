import { GestureTool, GestureToolView } from "./gesture_tool";
import { BoxAnnotation } from "../../annotations/box_annotation";
import { CartesianFrame } from "../../canvas/cartesian_frame";
import { GestureEvent } from "core/ui_events";
import { Dimensions } from "core/enums";
export declare class BoxZoomToolView extends GestureToolView {
    model: BoxZoomTool;
    protected _base_point: [number, number] | null;
    _match_aspect(base_point: [number, number], curpoint: [number, number], frame: CartesianFrame): [[number, number], [number, number]];
    protected _compute_limits(curpoint: [number, number]): [[number, number], [number, number]];
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    _update([sx0, sx1]: [number, number], [sy0, sy1]: [number, number]): void;
}
export declare namespace BoxZoomTool {
    interface Attrs extends GestureTool.Attrs {
        dimensions: Dimensions;
        overlay: BoxAnnotation;
        match_aspect: boolean;
        origin: "corner" | "center";
    }
    interface Props extends GestureTool.Props {
    }
}
export interface BoxZoomTool extends BoxZoomTool.Attrs {
}
export declare class BoxZoomTool extends GestureTool {
    properties: BoxZoomTool.Props;
    constructor(attrs?: Partial<BoxZoomTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "pan";
    default_order: number;
    readonly tooltip: string;
}
