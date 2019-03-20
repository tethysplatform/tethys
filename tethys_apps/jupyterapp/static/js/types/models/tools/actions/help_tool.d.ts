import { ActionTool, ActionToolView } from "./action_tool";
export declare class HelpToolView extends ActionToolView {
    model: HelpTool;
    doit(): void;
}
export declare namespace HelpTool {
    interface Attrs extends ActionTool.Attrs {
        help_tooltip: string;
        redirect: string;
    }
    interface Props extends ActionTool.Props {
    }
}
export interface HelpTool extends HelpTool.Attrs {
}
export declare class HelpTool extends ActionTool {
    properties: HelpTool.Props;
    constructor(attrs?: Partial<HelpTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    readonly tooltip: string;
}
