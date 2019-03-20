import { GestureTool, GestureToolView } from "./gesture_tool";
import { ScrollEvent } from "core/ui_events";
import { Dimension } from "core/enums";
export declare class WheelPanToolView extends GestureToolView {
    model: WheelPanTool;
    _scroll(ev: ScrollEvent): void;
    _update_ranges(factor: number): void;
}
export declare namespace WheelPanTool {
    interface Attrs extends GestureTool.Attrs {
        dimension: Dimension;
        speed: number;
    }
    interface Props extends GestureTool.Props {
    }
}
export interface WheelPanTool extends WheelPanTool.Attrs {
}
export declare class WheelPanTool extends GestureTool {
    properties: WheelPanTool.Props;
    constructor(attrs?: Partial<WheelPanTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "scroll";
    default_order: number;
    readonly tooltip: string;
}
