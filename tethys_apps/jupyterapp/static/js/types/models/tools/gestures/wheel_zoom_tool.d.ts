import { GestureTool, GestureToolView } from "./gesture_tool";
import { GestureEvent, ScrollEvent } from "core/ui_events";
import { Dimensions } from "core/enums";
export declare class WheelZoomToolView extends GestureToolView {
    model: WheelZoomTool;
    _pinch(ev: GestureEvent): void;
    _scroll(ev: ScrollEvent): void;
}
export declare namespace WheelZoomTool {
    interface Attrs extends GestureTool.Attrs {
        dimensions: Dimensions;
        maintain_focus: boolean;
        zoom_on_axis: boolean;
        speed: number;
    }
    interface Props extends GestureTool.Props {
    }
}
export interface WheelZoomTool extends WheelZoomTool.Attrs {
}
export declare class WheelZoomTool extends GestureTool {
    properties: WheelZoomTool.Props;
    constructor(attrs?: Partial<WheelZoomTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "scroll" | "pinch";
    default_order: number;
    readonly tooltip: string;
}
