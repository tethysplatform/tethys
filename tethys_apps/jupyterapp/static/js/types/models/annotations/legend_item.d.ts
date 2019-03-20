import { Model } from "../../model";
import { Legend } from "./legend";
import { GlyphRenderer } from "../renderers/glyph_renderer";
import { StringSpec } from "core/vectorization";
export declare namespace LegendItem {
    interface Attrs extends Model.Attrs {
        label: StringSpec | null;
        renderers: GlyphRenderer[];
        index: number | null;
    }
    interface Props extends Model.Props {
    }
}
export interface LegendItem extends LegendItem.Attrs {
}
export declare class LegendItem extends Model {
    properties: LegendItem.Props;
    legend: Legend | null;
    constructor(attrs?: Partial<LegendItem.Attrs>);
    static initClass(): void;
    protected _check_data_sources_on_renderers(): boolean;
    protected _check_field_label_on_data_source(): boolean;
    initialize(): void;
    get_field_from_label_prop(): string | null;
    get_labels_list_from_label_prop(): string[];
}
