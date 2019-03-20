import { SelectTool, SelectToolView } from "./select_tool";
import { PolyAnnotation } from "../../annotations/poly_annotation";
import { PolyGeometry } from "core/geometry";
import { TapEvent, KeyEvent } from "core/ui_events";
export declare class PolySelectToolView extends SelectToolView {
    model: PolySelectTool;
    protected data: {
        sx: number[];
        sy: number[];
    };
    initialize(options: any): void;
    connect_signals(): void;
    _active_change(): void;
    _keyup(ev: KeyEvent): void;
    _doubletap(ev: TapEvent): void;
    _clear_data(): void;
    _tap(ev: TapEvent): void;
    _do_select(sx: number[], sy: number[], final: boolean, append: boolean): void;
    _emit_callback(geometry: PolyGeometry): void;
}
export declare namespace PolySelectTool {
    interface Attrs extends SelectTool.Attrs {
        callback: any;
        overlay: PolyAnnotation;
    }
    interface Props extends SelectTool.Props {
    }
}
export interface PolySelectTool extends PolySelectTool.Attrs {
}
export declare class PolySelectTool extends SelectTool {
    properties: PolySelectTool.Props;
    constructor(attrs?: Partial<PolySelectTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: "tap";
    default_order: number;
}
