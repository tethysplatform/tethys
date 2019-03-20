import { GestureEvent, TapEvent, MoveEvent, KeyEvent, UIEvent } from "core/ui_events";
import { MultiLine } from "../../glyphs/multi_line";
import { Patches } from "../../glyphs/patches";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { PolyTool, PolyToolView } from "./poly_tool";
export interface HasPolyGlyph {
    glyph: MultiLine | Patches;
}
export declare class PolyEditToolView extends PolyToolView {
    model: PolyEditTool;
    _selected_renderer: GlyphRenderer | null;
    _basepoint: [number, number] | null;
    _drawing: boolean;
    _doubletap(ev: TapEvent): void;
    _show_vertices(ev: UIEvent): void;
    _move(ev: MoveEvent): void;
    _tap(ev: TapEvent): void;
    _remove_vertex(): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    _keyup(ev: KeyEvent): void;
    deactivate(): void;
}
export declare namespace PolyEditTool {
    interface Attrs extends PolyTool.Attrs {
    }
    interface Props extends PolyTool.Props {
    }
}
export interface PolyEditTool extends PolyEditTool.Attrs {
}
export declare class PolyEditTool extends PolyTool {
    properties: PolyEditTool.Props;
    constructor(attrs?: Partial<PolyEditTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: ("pan" | "tap" | "move")[];
    default_order: number;
}
