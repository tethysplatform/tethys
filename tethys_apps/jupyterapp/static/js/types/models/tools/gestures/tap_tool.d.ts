import { SelectTool, SelectToolView } from "./select_tool";
import { TapEvent } from "core/ui_events";
import { PointGeometry } from "core/geometry";
export declare class TapToolView extends SelectToolView {
    model: TapTool;
    _tap(ev: TapEvent): void;
    _select(geometry: PointGeometry, final: boolean, append: boolean): void;
}
export declare namespace TapTool {
    interface Attrs extends SelectTool.Attrs {
        behavior: "select" | "inspect";
        callback: any;
    }
    interface Props extends SelectTool.Props {
    }
}
export interface TapTool extends TapTool.Attrs {
}
export declare class TapTool extends SelectTool {
    properties: TapTool.Props;
    constructor(attrs?: Partial<TapTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "tap";
    default_order: number;
}
