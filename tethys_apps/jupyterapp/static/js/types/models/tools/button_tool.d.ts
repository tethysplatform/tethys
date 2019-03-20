import { Class } from "core/class";
import { DOMView } from "core/dom_view";
import { Tool, ToolView } from "./tool";
export declare abstract class ButtonToolButtonView extends DOMView {
    model: ButtonTool;
    initialize(options: any): void;
    css_classes(): string[];
    render(): void;
    protected abstract _clicked(): void;
}
export declare abstract class ButtonToolView extends ToolView {
    model: ButtonTool;
}
export declare namespace ButtonTool {
    interface Attrs extends Tool.Attrs {
        disabled: boolean;
    }
    interface Props extends Tool.Props {
    }
}
export interface ButtonTool extends ButtonTool.Attrs {
}
export declare abstract class ButtonTool extends Tool {
    properties: ButtonTool.Props;
    constructor(attrs?: Partial<ButtonTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    button_view: Class<ButtonToolButtonView>;
    readonly tooltip: string;
    readonly computed_icon: string;
}
