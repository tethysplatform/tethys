import { ActionTool, ActionToolView } from "./action_tool";
import { Dimensions } from "core/enums";
export declare class ZoomInToolView extends ActionToolView {
    model: ZoomInTool;
    doit(): void;
}
export declare namespace ZoomInTool {
    interface Attrs extends ActionTool.Attrs {
        factor: number;
        dimensions: Dimensions;
    }
    interface Props extends ActionTool.Props {
    }
}
export interface ZoomInTool extends ZoomInTool.Attrs {
}
export declare class ZoomInTool extends ActionTool {
    properties: ZoomInTool.Props;
    constructor(attrs?: Partial<ZoomInTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    readonly tooltip: string;
}
