import { Tool } from "./tool";
import { GestureTool } from "./gestures/gesture_tool";
import { ToolbarBase } from "./toolbar_base";
export declare type Drag = Tool;
export declare type Inspection = Tool;
export declare type Scroll = Tool;
export declare type Tap = Tool;
export declare namespace Toolbar {
    interface Attrs extends ToolbarBase.Attrs {
        active_drag: Drag | "auto";
        active_inspect: Inspection | Inspection[] | "auto";
        active_scroll: Scroll | "auto";
        active_tap: Tap | "auto";
        active_multi: GestureTool;
    }
    interface Props extends ToolbarBase.Props {
    }
}
export interface Toolbar extends Toolbar.Attrs {
}
export declare class Toolbar extends ToolbarBase {
    properties: Toolbar.Props;
    constructor(attrs?: Partial<Toolbar.Attrs>);
    static initClass(): void;
    initialize(): void;
    connect_signals(): void;
    protected _init_tools(): void;
}
