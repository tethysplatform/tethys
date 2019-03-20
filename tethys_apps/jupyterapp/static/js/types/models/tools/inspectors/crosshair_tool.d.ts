import { InspectTool, InspectToolView } from "./inspect_tool";
import { Renderer } from "../../renderers/renderer";
import { Span } from "../../annotations/span";
import { Dimensions, SpatialUnits, RenderMode } from "core/enums";
import { MoveEvent } from "core/ui_events";
import { Color } from "core/types";
export declare class CrosshairToolView extends InspectToolView {
    model: CrosshairTool;
    _move(ev: MoveEvent): void;
    _move_exit(_e: MoveEvent): void;
    _update_spans(x: number | null, y: number | null): void;
}
export declare namespace CrosshairTool {
    interface Attrs extends InspectTool.Attrs {
        dimensions: Dimensions;
        line_color: Color;
        line_width: number;
        line_alpha: number;
        location_units: SpatialUnits;
        render_mode: RenderMode;
        spans: {
            width: Span;
            height: Span;
        };
    }
    interface Props extends InspectTool.Props {
    }
}
export interface CrosshairTool extends CrosshairTool.Attrs {
}
export declare class CrosshairTool extends InspectTool {
    properties: CrosshairTool.Props;
    constructor(attrs?: Partial<CrosshairTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    readonly tooltip: string;
    readonly synthetic_renderers: Renderer[];
    initialize(): void;
}
