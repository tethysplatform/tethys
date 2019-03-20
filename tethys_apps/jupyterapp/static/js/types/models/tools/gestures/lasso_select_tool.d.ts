import { SelectTool, SelectToolView } from "./select_tool";
import { PolyAnnotation } from "../../annotations/poly_annotation";
import { PolyGeometry } from "core/geometry";
import { GestureEvent, KeyEvent } from "core/ui_events";
export declare class LassoSelectToolView extends SelectToolView {
    model: LassoSelectTool;
    protected data: {
        sx: number[];
        sy: number[];
    } | null;
    initialize(options: any): void;
    connect_signals(): void;
    _active_change(): void;
    _keyup(ev: KeyEvent): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    _clear_overlay(): void;
    _do_select(sx: number[], sy: number[], final: boolean, append: boolean): void;
    _emit_callback(geometry: PolyGeometry): void;
}
export declare namespace LassoSelectTool {
    interface Attrs extends SelectTool.Attrs {
        select_every_mousemove: boolean;
        callback: any;
        overlay: PolyAnnotation;
    }
    interface Props extends SelectTool.Props {
    }
}
export interface LassoSelectTool extends LassoSelectTool.Attrs {
}
export declare class LassoSelectTool extends SelectTool {
    properties: LassoSelectTool.Props;
    constructor(attrs?: Partial<LassoSelectTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "pan";
    default_order: number;
}
