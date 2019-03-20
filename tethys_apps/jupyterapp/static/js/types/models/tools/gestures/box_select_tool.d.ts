import { SelectTool, SelectToolView } from "./select_tool";
import { BoxAnnotation } from "../../annotations/box_annotation";
import { Dimensions } from "core/enums";
import { GestureEvent } from "core/ui_events";
import { RectGeometry } from "core/geometry";
export declare class BoxSelectToolView extends SelectToolView {
    model: BoxSelectTool;
    protected _base_point: [number, number] | null;
    protected _compute_limits(curpoint: [number, number]): [[number, number], [number, number]];
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    _do_select([sx0, sx1]: [number, number], [sy0, sy1]: [number, number], final: boolean, append?: boolean): void;
    _emit_callback(geometry: RectGeometry): void;
}
export declare namespace BoxSelectTool {
    interface Attrs extends SelectTool.Attrs {
        dimensions: Dimensions;
        select_every_mousemove: boolean;
        callback: any;
        overlay: BoxAnnotation;
        origin: "corner" | "center";
    }
    interface Props extends SelectTool.Props {
    }
}
export interface BoxSelectTool extends BoxSelectTool.Attrs {
}
export declare class BoxSelectTool extends SelectTool {
    properties: BoxSelectTool.Props;
    constructor(attrs?: Partial<BoxSelectTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "pan";
    default_order: number;
    readonly tooltip: string;
}
