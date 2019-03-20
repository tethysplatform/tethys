import { Model } from "../../model";
import * as p from "core/properties";
import { Glyph, GlyphView } from "../glyphs/glyph";
export declare namespace Selection {
    interface Attrs extends Model.Attrs {
        indices: number[];
        final: boolean;
        line_indices: number[];
        selected_glyphs: Glyph[];
        get_view: () => GlyphView | null;
        multiline_indices: {
            [key: string]: number[];
        };
    }
    interface Props extends Model.Props {
        indices: p.Property<number[]>;
        final: p.Property<boolean>;
        line_indices: p.Property<number[]>;
        selected_glyphs: p.Property<Glyph[]>;
        get_view: p.Property<() => GlyphView | null>;
        multiline_indices: p.Property<{
            [key: string]: number[];
        }>;
    }
}
export interface Selection extends Selection.Attrs {
}
export declare class Selection extends Model {
    properties: Selection.Props;
    constructor(attrs?: Partial<Selection.Attrs>);
    static initClass(): void;
    [key: string]: any;
    initialize(): void;
    readonly selected_glyph: Glyph | null;
    add_to_selected_glyphs(glyph: Glyph): void;
    update(selection: Selection, final: boolean, append: boolean): void;
    clear(): void;
    is_empty(): boolean;
    update_through_union(other: Selection): void;
    update_through_intersection(other: Selection): void;
}
