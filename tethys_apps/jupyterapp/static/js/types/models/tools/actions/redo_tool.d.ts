import { ActionTool, ActionToolView } from "./action_tool";
export declare class RedoToolView extends ActionToolView {
    model: RedoTool;
    connect_signals(): void;
    doit(): void;
}
export declare namespace RedoTool {
    interface Attrs extends ActionTool.Attrs {
    }
    interface Props extends ActionTool.Props {
    }
}
export interface RedoTool extends RedoTool.Attrs {
}
export declare class RedoTool extends ActionTool {
    properties: RedoTool.Props;
    constructor(attrs?: Partial<RedoTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
}
