import * as p from "core/properties";
import { DOMView } from "core/dom_view";
import { Logo, Location } from "core/enums";
import { Model } from "model";
import { Tool } from "./tool";
import { ButtonToolButtonView } from "./button_tool";
import { GestureTool } from "./gestures/gesture_tool";
import { ActionTool } from "./actions/action_tool";
import { HelpTool } from "./actions/help_tool";
import { ToolProxy } from "./tool_proxy";
import { InspectTool } from "./inspectors/inspect_tool";
export declare class ToolbarBaseView extends DOMView {
    model: ToolbarBase;
    protected _tool_button_views: {
        [key: string]: ButtonToolButtonView;
    };
    initialize(options: any): void;
    connect_signals(): void;
    remove(): void;
    protected _build_tool_button_views(): void;
    render(): void;
}
export declare type GestureType = "pan" | "scroll" | "pinch" | "tap" | "doubletap" | "press" | "rotate" | "move" | "multi";
export declare namespace ToolbarBase {
    interface Attrs extends Model.Attrs {
        tools: Tool[];
        logo: Logo;
        gestures: {
            pan: {
                tools: GestureTool[];
                active: Tool | null;
            };
            scroll: {
                tools: GestureTool[];
                active: Tool | null;
            };
            pinch: {
                tools: GestureTool[];
                active: Tool | null;
            };
            tap: {
                tools: GestureTool[];
                active: Tool | null;
            };
            doubletap: {
                tools: GestureTool[];
                active: Tool | null;
            };
            press: {
                tools: GestureTool[];
                active: Tool | null;
            };
            rotate: {
                tools: GestureTool[];
                active: Tool | null;
            };
            move: {
                tools: GestureTool[];
                active: Tool | null;
            };
            multi: {
                tools: GestureTool[];
                active: Tool | null;
            };
        };
        actions: ActionTool[];
        inspectors: InspectTool[];
        help: HelpTool[];
        toolbar_location: Location;
    }
    interface Props extends Model.Props {
        tools: p.Property<Tool[]>;
    }
}
export interface ToolbarBase extends ToolbarBase.Attrs {
}
export declare class ToolbarBase extends Model {
    properties: ToolbarBase.Props;
    constructor(attrs?: Partial<ToolbarBase.Attrs>);
    static initClass(): void;
    _proxied_tools?: (Tool | ToolProxy)[];
    readonly horizontal: boolean;
    readonly vertical: boolean;
    _active_change(tool: Tool): void;
}
