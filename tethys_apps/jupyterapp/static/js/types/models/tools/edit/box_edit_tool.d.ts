import { GestureEvent, TapEvent, KeyEvent, UIEvent, MoveEvent } from "core/ui_events";
import { Dimensions } from "core/enums";
import { Rect } from "../../glyphs/rect";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { ColumnDataSource } from "../../sources/column_data_source";
import { EditTool, EditToolView } from "./edit_tool";
export interface HasRectCDS {
    glyph: Rect;
    data_source: ColumnDataSource;
}
export declare class BoxEditToolView extends EditToolView {
    model: BoxEditTool;
    _draw_basepoint: [number, number] | null;
    _tap(ev: TapEvent): void;
    _keyup(ev: KeyEvent): void;
    _set_extent([sx0, sx1]: [number, number], [sy0, sy1]: [number, number], append: boolean, emit?: boolean): void;
    _update_box(ev: UIEvent, append?: boolean, emit?: boolean): void;
    _doubletap(ev: TapEvent): void;
    _move(ev: MoveEvent): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent, append?: boolean, emit?: boolean): void;
    _pan_end(ev: GestureEvent): void;
}
export declare namespace BoxEditTool {
    interface Attrs extends EditTool.Attrs {
        dimensions: Dimensions;
        num_objects: number;
        renderers: (GlyphRenderer & HasRectCDS)[];
    }
    interface Props extends EditTool.Props {
    }
}
export interface BoxEditTool extends BoxEditTool.Attrs {
}
export declare class BoxEditTool extends EditTool {
    properties: BoxEditTool.Props;
    renderers: (GlyphRenderer & HasRectCDS)[];
    constructor(attrs?: Partial<BoxEditTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: ("pan" | "tap" | "move")[];
    default_order: number;
}
