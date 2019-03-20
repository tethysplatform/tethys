import { Constraint, Variable } from "core/layout/solver";
import * as visuals from "core/visuals";
import * as p from "core/properties";
import { Signal0 } from "core/signaling";
import { Color } from "core/types";
import { LineJoin, LineCap } from "core/enums";
import { Place, Location, OutputBackend } from "core/enums";
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
import { Title } from "../annotations/title";
import { Toolbar } from "../tools/toolbar";
import { PlotCanvas, PlotCanvasView } from "./plot_canvas";
import { Range } from "../ranges/range";
import { Scale } from "../scales/scale";
import { Glyph } from "../glyphs/glyph";
import { DataSource } from "../sources/data_source";
import { Renderer } from "../renderers/renderer";
import { GlyphRenderer } from "../renderers/glyph_renderer";
import { Tool } from "../tools/tool";
export declare class PlotView extends LayoutDOMView {
    model: Plot;
    connect_signals(): void;
    css_classes(): string[];
    get_height(): number;
    get_width(): number;
    save(name: string): void;
    readonly plot_canvas_view: PlotCanvasView;
}
export declare namespace Plot {
    interface OutlineLine {
        outline_line_color: Color;
        outline_line_width: number;
        outline_line_alpha: number;
        outline_line_join: LineJoin;
        outline_line_cap: LineCap;
        outline_line_dash: number[];
        outline_line_dash_offset: number;
    }
    interface BackgroundFill {
        background_fill_color: Color;
        background_fill_alpha: number;
    }
    interface BorderFill {
        border_fill_color: Color;
        border_fill_alpha: number;
    }
    interface Mixins extends OutlineLine, BackgroundFill, BorderFill {
    }
    interface Attrs extends LayoutDOM.Attrs, Mixins {
        toolbar: Toolbar;
        toolbar_location: Location | null;
        toolbar_sticky: boolean;
        plot_width: number;
        plot_height: number;
        title: Title | string | null;
        title_location: Location;
        h_symmetry: boolean;
        v_symmetry: boolean;
        above: Renderer[];
        below: Renderer[];
        left: Renderer[];
        right: Renderer[];
        renderers: Renderer[];
        x_range: Range;
        extra_x_ranges: {
            [key: string]: Range;
        };
        y_range: Range;
        extra_y_ranges: {
            [key: string]: Range;
        };
        x_scale: Scale;
        y_scale: Scale;
        lod_factor: number;
        lod_interval: number;
        lod_threshold: number;
        lod_timeout: number;
        hidpi: boolean;
        output_backend: OutputBackend;
        min_border: number | null;
        min_border_top: number | null;
        min_border_left: number | null;
        min_border_bottom: number | null;
        min_border_right: number | null;
        inner_width: number;
        inner_height: number;
        layout_width: number;
        layout_height: number;
        match_aspect: boolean;
        aspect_scale: number;
    }
    interface Props extends LayoutDOM.Props {
        toolbar_location: p.Property<Location | null>;
        title: p.Property<Title | string | null>;
        above: p.Property<Renderer[]>;
        below: p.Property<Renderer[]>;
        left: p.Property<Renderer[]>;
        right: p.Property<Renderer[]>;
        renderers: p.Property<Renderer[]>;
        outline_line_width: p.Property<number>;
    }
    type Visuals = visuals.Visuals & {
        outline_line: visuals.Line;
        background_fill: visuals.Fill;
        border_fill: visuals.Fill;
    };
}
export interface Plot extends Plot.Attrs {
}
export declare class Plot extends LayoutDOM {
    reset: Signal0<this>;
    properties: Plot.Props;
    constructor(attrs?: Partial<Plot.Attrs>);
    static initClass(): void;
    protected _plot_canvas: PlotCanvas;
    initialize(): void;
    protected _init_plot_canvas(): PlotCanvas;
    protected _init_title_panel(): void;
    protected _init_toolbar_panel(): void;
    connect_signals(): void;
    readonly plot_canvas: PlotCanvas;
    protected _doc_attached(): void;
    add_renderers(...new_renderers: Renderer[]): void;
    add_layout(renderer: any, side?: Place): void;
    remove_layout(renderer: Renderer): void;
    add_glyph(glyph: Glyph, source?: DataSource, extra_attrs?: any): GlyphRenderer;
    add_tools(...tools: Tool[]): void;
    get_layoutable_children(): LayoutDOM[];
    get_constraints(): Constraint[];
    get_constrained_variables(): {
        [key: string]: Variable;
    };
    readonly all_renderers: Renderer[];
}
