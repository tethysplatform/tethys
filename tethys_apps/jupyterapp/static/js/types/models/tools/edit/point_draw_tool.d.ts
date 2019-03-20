import { GestureEvent, TapEvent, KeyEvent } from "core/ui_events";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { EditTool, EditToolView, HasXYGlyph } from "./edit_tool";
export declare class PointDrawToolView extends EditToolView {
    model: PointDrawTool;
    _tap(ev: TapEvent): void;
    _keyup(ev: KeyEvent): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
}
export declare namespace PointDrawTool {
    interface Attrs extends EditTool.Attrs {
        add: boolean;
        drag: boolean;
        num_objects: number;
        renderers: (GlyphRenderer & HasXYGlyph)[];
    }
    interface Props extends EditTool.Props {
    }
}
export interface PointDrawTool extends PointDrawTool.Attrs {
}
export declare class PointDrawTool extends EditTool {
    properties: PointDrawTool.Props;
    renderers: (GlyphRenderer & HasXYGlyph)[];
    constructor(attrs?: Partial<PointDrawTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: ("pan" | "tap" | "move")[];
    default_order: number;
}
