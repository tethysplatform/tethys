import { ActionTool, ActionToolView } from "./action_tool";
export declare class SaveToolView extends ActionToolView {
    model: SaveTool;
    doit(): void;
}
export declare namespace SaveTool {
    interface Attrs extends ActionTool.Attrs {
    }
    interface Props extends ActionTool.Props {
    }
}
export interface SaveTool extends SaveTool.Attrs {
}
export declare class SaveTool extends ActionTool {
    properties: SaveTool.Props;
    constructor(attrs?: Partial<SaveTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
}
