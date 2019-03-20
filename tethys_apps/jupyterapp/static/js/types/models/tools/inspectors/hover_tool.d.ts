import { InspectTool, InspectToolView } from "./inspect_tool";
import { Tooltip, TooltipView } from "../../annotations/tooltip";
import { RendererView } from "../../renderers/renderer";
import { DataRenderer, RendererSpec } from "../util";
import { MoveEvent } from "core/ui_events";
import { Vars } from "core/util/templating";
import * as p from "core/properties";
import { Anchor, TooltipAttachment } from "core/enums";
import { Geometry, PointGeometry, SpanGeometry } from "core/geometry";
import { ColumnarDataSource } from "../../sources/columnar_data_source";
import { ImageIndex } from "../../glyphs/image";
export declare function _nearest_line_hit(i: number, geometry: Geometry, sx: number, sy: number, dx: number[], dy: number[]): [[number, number], number];
export declare function _line_hit(xs: number[], ys: number[], ind: number): [[number, number], number];
export declare class HoverToolView extends InspectToolView {
    model: HoverTool;
    protected ttviews: {
        [key: string]: TooltipView;
    };
    protected _ttmodels: {
        [key: string]: Tooltip;
    } | null;
    protected _computed_renderers: DataRenderer[] | null;
    initialize(options: any): void;
    remove(): void;
    connect_signals(): void;
    protected _compute_ttmodels(): {
        [key: string]: Tooltip;
    };
    readonly computed_renderers: DataRenderer[];
    readonly ttmodels: {
        [key: string]: Tooltip;
    };
    _clear(): void;
    _move(ev: MoveEvent): void;
    _move_exit(): void;
    _inspect(sx: number, sy: number): void;
    _update([renderer_view, { geometry }]: [RendererView, {
        geometry: PointGeometry | SpanGeometry;
    }]): void;
    _emit_callback(geometry: PointGeometry | SpanGeometry): void;
    _render_tooltips(ds: ColumnarDataSource, i: number | ImageIndex, vars: Vars): HTMLElement;
}
export declare namespace HoverTool {
    interface Attrs extends InspectTool.Attrs {
        tooltips: string | [string, string][] | ((source: ColumnarDataSource, vars: Vars) => HTMLElement);
        formatters: any;
        renderers: RendererSpec;
        names: string[];
        mode: "mouse" | "hline" | "vline";
        point_policy: "snap_to_data" | "follow_mouse" | "none";
        line_policy: "prev" | "next" | "nearest" | "interp" | "none";
        show_arrow: boolean;
        anchor: Anchor;
        attachment: TooltipAttachment;
        callback: any;
    }
    interface Props extends InspectTool.Props {
        tooltips: p.Property<string | [string, string][] | ((source: ColumnarDataSource, vars: Vars) => HTMLElement)>;
        renderers: p.Property<RendererSpec>;
        names: p.Property<string[]>;
    }
}
export interface HoverTool extends HoverTool.Attrs {
}
export declare class HoverTool extends InspectTool {
    properties: HoverTool.Props;
    constructor(attrs?: Partial<HoverTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
}
