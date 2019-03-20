import { ActionTool, ActionToolView, ActionToolButtonView } from "./action_tool";
export declare class CustomActionButtonView extends ActionToolButtonView {
    model: CustomAction;
    css_classes(): string[];
}
export declare class CustomActionView extends ActionToolView {
    model: CustomAction;
    doit(): void;
}
export declare namespace CustomAction {
    interface Attrs extends ActionTool.Attrs {
        action_tooltip: string;
        callback: any;
        icon: string;
    }
    interface Props extends ActionTool.Props {
    }
}
export interface CustomAction extends CustomAction.Attrs {
}
export declare class CustomAction extends ActionTool {
    properties: CustomAction.Props;
    constructor(attrs?: Partial<CustomAction.Attrs>);
    static initClass(): void;
    tool_name: string;
    button_view: typeof CustomActionButtonView;
    readonly tooltip: string;
}
