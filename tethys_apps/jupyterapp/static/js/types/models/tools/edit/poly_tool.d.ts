import { UIEvent } from "core/ui_events";
import { MultiLine } from "../../glyphs/multi_line";
import { Patches } from "../../glyphs/patches";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { EditTool, EditToolView, HasXYGlyph } from "./edit_tool";
export interface HasPolyGlyph {
    glyph: MultiLine | Patches;
}
export declare class PolyToolView extends EditToolView {
    model: PolyTool;
    _set_vertices(xs: number[] | number, ys: number[] | number): void;
    _hide_vertices(): void;
    _snap_to_vertex(ev: UIEvent, x: number, y: number): [number, number];
}
export declare namespace PolyTool {
    interface Attrs extends EditTool.Attrs {
        renderers: (GlyphRenderer & HasPolyGlyph)[];
        vertex_renderer: (GlyphRenderer & HasXYGlyph);
    }
    interface Props extends EditTool.Props {
    }
}
export interface PolyTool extends PolyTool.Attrs {
}
export declare class PolyTool extends EditTool {
    properties: PolyTool.Props;
    renderers: (GlyphRenderer & HasPolyGlyph)[];
    constructor(attrs?: Partial<PolyTool.Attrs>);
    static initClass(): void;
}
