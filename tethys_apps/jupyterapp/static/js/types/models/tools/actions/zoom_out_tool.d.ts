import { ActionTool, ActionToolView } from "./action_tool";
import { Dimensions } from "core/enums";
export declare class ZoomOutToolView extends ActionToolView {
    model: ZoomOutTool;
    doit(): void;
}
export declare namespace ZoomOutTool {
    interface Attrs extends ActionTool.Attrs {
        factor: number;
        dimensions: Dimensions;
    }
    interface Props extends ActionTool.Props {
    }
}
export interface ZoomOutTool extends ZoomOutTool.Attrs {
}
export declare class ZoomOutTool extends ActionTool {
    properties: ZoomOutTool.Props;
    constructor(attrs?: Partial<ZoomOutTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    readonly tooltip: string;
}
