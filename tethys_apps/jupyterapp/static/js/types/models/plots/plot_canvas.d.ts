import { Canvas, CanvasView } from "../canvas/canvas";
import { CartesianFrame } from "../canvas/cartesian_frame";
import { Range } from "../ranges/range";
import { RendererView } from "../renderers/renderer";
import { LayoutDOM } from "../layouts/layout_dom";
import { Toolbar } from "../tools/toolbar";
import { ToolView } from "../tools/tool";
import { Selection } from "../selections/selection";
import { Plot } from "./plot";
import { Arrayable } from "core/types";
import { Signal0 } from "core/signaling";
import { UIEvents } from "core/ui_events";
import { DOMView } from "core/dom_view";
import { LayoutCanvas } from "core/layout/layout_canvas";
import { Constraint } from "core/layout/solver";
import { Context2d } from "core/util/canvas";
export declare type WebGLState = {
    canvas: HTMLCanvasElement;
    ctx: WebGLRenderingContext;
};
export declare type FrameBox = [number, number, number, number];
export declare type Interval = {
    start: number;
    end: number;
};
export declare type RangeInfo = {
    xrs: {
        [key: string]: Interval;
    };
    yrs: {
        [key: string]: Interval;
    };
};
export declare type StateInfo = {
    range?: RangeInfo;
    selection: {
        [key: string]: Selection;
    };
    dimensions: {
        width: number;
        height: number;
    };
};
export declare class PlotCanvasView extends DOMView {
    model: PlotCanvas;
    visuals: Plot.Visuals;
    canvas_view: CanvasView;
    gl?: WebGLState;
    force_paint: Signal0<this>;
    state_changed: Signal0<this>;
    protected _is_paused?: number;
    protected lod_started: boolean;
    protected _initial_state_info: StateInfo;
    protected state: {
        history: {
            type: string;
            info: StateInfo;
        }[];
        index: number;
    };
    protected throttled_paint: () => void;
    protected ui_event_bus: UIEvents;
    protected levels: {
        [key: string]: {
            [key: string]: RendererView;
        };
    };
    renderer_views: {
        [key: string]: RendererView;
    };
    protected tool_views: {
        [key: string]: ToolView;
    };
    protected range_update_timestamp?: number;
    readonly frame: CartesianFrame;
    readonly canvas: Canvas;
    readonly canvas_overlays: HTMLElement;
    readonly canvas_events: HTMLElement;
    readonly is_paused: boolean;
    view_options(): {
        [key: string]: any;
    };
    pause(): void;
    unpause(no_render?: boolean): void;
    request_render(): void;
    request_paint(): void;
    reset(): void;
    remove(): void;
    css_classes(): string[];
    initialize(options: any): void;
    set_cursor(cursor?: string): void;
    init_webgl(): void;
    prepare_webgl(ratio: number, frame_box: FrameBox): void;
    blit_webgl(ratio: number): void;
    update_dataranges(): void;
    map_to_screen(x: Arrayable<number>, y: Arrayable<number>, x_name?: string, y_name?: string): [Arrayable<number>, Arrayable<number>];
    push_state(type: string, new_info: Partial<StateInfo>): void;
    clear_state(): void;
    can_undo(): void;
    can_redo(): void;
    undo(): void;
    redo(): void;
    protected _do_state_change(index: number): void;
    get_selection(): {
        [key: string]: Selection;
    };
    update_selection(selection: {
        [key: string]: Selection;
    } | null): void;
    reset_selection(): void;
    protected _update_ranges_together(range_info_iter: [Range, Interval][]): void;
    protected _update_ranges_individually(range_info_iter: [Range, Interval][], is_panning: boolean, is_scrolling: boolean, maintain_focus: boolean): void;
    protected _get_weight_to_constrain_interval(rng: Range, range_info: Interval): number;
    update_range(range_info: RangeInfo | null, is_panning?: boolean, is_scrolling?: boolean, maintain_focus?: boolean): void;
    reset_range(): void;
    build_levels(): void;
    get_renderer_views(): RendererView[];
    build_tools(): void;
    connect_signals(): void;
    set_initial_range(): void;
    update_constraints(): void;
    protected _layout(final?: boolean): void;
    has_finished(): boolean;
    render(): void;
    protected _needs_layout(): boolean;
    repaint(): void;
    paint(): void;
    protected _paint_levels(ctx: Context2d, levels: string[], clip_region: FrameBox, global_clip: boolean): void;
    protected _map_hook(_ctx: Context2d, _frame_box: FrameBox): void;
    protected _paint_empty(ctx: Context2d, frame_box: FrameBox): void;
    save(name: string): void;
}
export declare class AbovePanel extends LayoutCanvas {
    static initClass(): void;
}
export declare class BelowPanel extends LayoutCanvas {
    static initClass(): void;
}
export declare class LeftPanel extends LayoutCanvas {
    static initClass(): void;
}
export declare class RightPanel extends LayoutCanvas {
    static initClass(): void;
}
export declare namespace PlotCanvas {
    interface Attrs extends LayoutDOM.Attrs {
        plot: Plot;
        toolbar: Toolbar;
        canvas: Canvas;
        frame: CartesianFrame;
    }
    interface Props extends LayoutDOM.Props {
    }
}
export interface PlotCanvas extends PlotCanvas.Attrs {
    use_map: boolean;
}
export declare class PlotCanvas extends LayoutDOM {
    properties: PlotCanvas.Props;
    constructor(attrs?: Partial<PlotCanvas.Attrs>);
    static initClass(): void;
    frame: CartesianFrame;
    canvas: Canvas;
    protected above_panel: AbovePanel;
    protected below_panel: BelowPanel;
    protected left_panel: LeftPanel;
    protected right_panel: RightPanel;
    initialize(): void;
    protected _doc_attached(): void;
    get_layoutable_children(): LayoutDOM[];
    get_constraints(): Constraint[];
    private _get_constant_constraints;
    private _get_side_constraints;
}
