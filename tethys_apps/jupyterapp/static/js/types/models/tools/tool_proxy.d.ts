import * as p from "core/properties";
import { EventType } from "core/ui_events";
import { Signal0 } from "core/signaling";
import { Class } from "core/class";
import { Model } from "../../model";
import { ButtonTool, ButtonToolButtonView } from "./button_tool";
export declare namespace ToolProxy {
    interface Attrs extends Model.Attrs {
        tools: ButtonTool[];
        active: boolean;
        disabled: boolean;
    }
    interface Props extends Model.Props {
        tools: p.Property<ButtonTool[]>;
        active: p.Property<boolean>;
        disabled: p.Property<boolean>;
    }
}
export interface ToolProxy extends ToolProxy.Attrs {
}
export declare class ToolProxy extends Model {
    properties: ToolProxy.Props;
    constructor(attrs?: Partial<ToolProxy.Attrs>);
    static initClass(): void;
    do: Signal0<this>;
    readonly button_view: Class<ButtonToolButtonView>;
    readonly event_type: undefined | EventType | EventType[];
    readonly tooltip: string;
    readonly tool_name: string;
    readonly icon: string;
    readonly computed_icon: string;
    initialize(): void;
    connect_signals(): void;
    doit(): void;
    set_active(): void;
}
