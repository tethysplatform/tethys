import { Renderer, RendererView } from "./renderer";
import { Glyph, GlyphView } from "../glyphs/glyph";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { Scale } from "../scales/scale";
import { CDSView } from "../sources/cds_view";
import * as p from "core/properties";
import * as hittest from "core/hittest";
import { Geometry } from "core/geometry";
import { SelectionManager } from "core/selection_manager";
import { Context2d } from "core/util/canvas";
export declare class GlyphRendererView extends RendererView {
    model: GlyphRenderer;
    glyph: GlyphView;
    selection_glyph: GlyphView;
    nonselection_glyph: GlyphView;
    hover_glyph?: GlyphView;
    muted_glyph?: GlyphView;
    decimated_glyph: GlyphView;
    xscale: Scale;
    yscale: Scale;
    protected all_indices: number[];
    protected decimated: number[];
    set_data_timestamp: number;
    protected last_dtrender: number;
    initialize(options: any): void;
    build_glyph_view<T extends Glyph>(model: T): GlyphView;
    connect_signals(): void;
    have_selection_glyphs(): boolean;
    set_data(request_render?: boolean, indices?: number[] | null): void;
    render(): void;
    draw_legend(ctx: Context2d, x0: number, x1: number, y0: number, y1: number, field: string | null, label: string, index: number | null): void;
    hit_test(geometry: Geometry): hittest.HitTestResult;
}
export declare namespace GlyphRenderer {
    interface Attrs extends Renderer.Attrs {
        x_range_name: string;
        y_range_name: string;
        data_source: ColumnarDataSource;
        view: CDSView;
        glyph: Glyph;
        hover_glyph: Glyph;
        nonselection_glyph: Glyph | "auto";
        selection_glyph: Glyph | "auto";
        muted_glyph: Glyph;
        muted: boolean;
    }
    interface Props extends Renderer.Props {
        view: p.Property<CDSView>;
    }
}
export interface GlyphRenderer extends GlyphRenderer.Attrs {
}
export declare class GlyphRenderer extends Renderer {
    properties: GlyphRenderer.Props;
    constructor(attrs?: Partial<GlyphRenderer.Attrs>);
    static initClass(): void;
    initialize(): void;
    get_reference_point(field: string | null, value: any): number;
    get_selection_manager(): SelectionManager;
}
