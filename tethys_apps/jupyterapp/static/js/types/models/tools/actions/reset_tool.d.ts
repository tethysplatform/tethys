import { ActionTool, ActionToolView } from "./action_tool";
export declare class ResetToolView extends ActionToolView {
    model: ResetTool;
    doit(): void;
}
export declare namespace ResetTool {
    interface Attrs extends ActionTool.Attrs {
    }
    interface Props extends ActionTool.Props {
    }
}
export interface ResetTool extends ResetTool.Attrs {
}
export declare class ResetTool extends ActionTool {
    properties: ResetTool.Props;
    constructor(attrs?: Partial<ResetTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
}
