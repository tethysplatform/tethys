import { UIEvent, GestureEvent, TapEvent, MoveEvent, KeyEvent } from "core/ui_events";
import { MultiLine } from "../../glyphs/multi_line";
import { Patches } from "../../glyphs/patches";
import { PolyTool, PolyToolView } from "./poly_tool";
export interface HasPolyGlyph {
    glyph: MultiLine | Patches;
}
export declare class PolyDrawToolView extends PolyToolView {
    model: PolyDrawTool;
    _drawing: boolean;
    _initialized: boolean;
    _tap(ev: TapEvent): void;
    _draw(ev: UIEvent, mode: string, emit?: boolean): void;
    _show_vertices(): void;
    _doubletap(ev: TapEvent): void;
    _move(ev: MoveEvent): void;
    _remove(): void;
    _keyup(ev: KeyEvent): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    activate(): void;
    deactivate(): void;
}
export declare namespace PolyDrawTool {
    interface Attrs extends PolyTool.Attrs {
        drag: boolean;
        num_objects: number;
    }
    interface Props extends PolyTool.Props {
    }
}
export interface PolyDrawTool extends PolyDrawTool.Attrs {
}
export declare class PolyDrawTool extends PolyTool {
    properties: PolyDrawTool.Props;
    constructor(attrs?: Partial<PolyDrawTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: ("pan" | "tap" | "move")[];
    default_order: number;
}
