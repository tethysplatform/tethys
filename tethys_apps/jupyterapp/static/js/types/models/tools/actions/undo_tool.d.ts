import { ActionTool, ActionToolView } from "./action_tool";
export declare class UndoToolView extends ActionToolView {
    model: UndoTool;
    connect_signals(): void;
    doit(): void;
}
export declare namespace UndoTool {
    interface Attrs extends ActionTool.Attrs {
    }
    interface Props extends ActionTool.Props {
    }
}
export interface UndoTool extends UndoTool.Attrs {
}
export declare class UndoTool extends ActionTool {
    properties: UndoTool.Props;
    constructor(attrs?: Partial<UndoTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
}
