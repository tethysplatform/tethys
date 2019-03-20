import { GestureTool, GestureToolView } from "./gesture_tool";
import { GestureEvent } from "core/ui_events";
import { Dimensions } from "core/enums";
export declare class PanToolView extends GestureToolView {
    model: PanTool;
    protected last_dx: number;
    protected last_dy: number;
    protected v_axis_only: boolean;
    protected h_axis_only: boolean;
    protected pan_info: {
        xrs: {
            [key: string]: {
                start: number;
                end: number;
            };
        };
        yrs: {
            [key: string]: {
                start: number;
                end: number;
            };
        };
        sdx: number;
        sdy: number;
    };
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(_e: GestureEvent): void;
    _update(dx: number, dy: number): void;
}
export declare namespace PanTool {
    interface Attrs extends GestureTool.Attrs {
        dimensions: Dimensions;
    }
    interface Props extends GestureTool.Props {
    }
}
export interface PanTool extends PanTool.Attrs {
}
export declare class PanTool extends GestureTool {
    properties: PanTool.Props;
    constructor(attrs?: Partial<PanTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    event_type: "pan";
    default_order: number;
    readonly tooltip: string;
    readonly icon: string;
}
