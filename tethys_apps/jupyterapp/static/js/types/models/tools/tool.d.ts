import * as p from "core/properties";
import { View } from "core/view";
import { Dimensions } from "core/enums";
import { Model } from "../../model";
import { Renderer } from "../renderers/renderer";
import { CartesianFrame } from "../canvas/cartesian_frame";
import { PlotCanvas, PlotCanvasView } from "../plots/plot_canvas";
import { EventType, GestureEvent, ScrollEvent, TapEvent, MoveEvent, KeyEvent } from "core/ui_events";
export declare abstract class ToolView extends View {
    model: Tool;
    plot_view: PlotCanvasView;
    initialize(options: any): void;
    readonly plot_model: PlotCanvas;
    connect_signals(): void;
    activate(): void;
    deactivate(): void;
    _pan_start?(e: GestureEvent): void;
    _pan?(e: GestureEvent): void;
    _pan_end?(e: GestureEvent): void;
    _pinch_start?(e: GestureEvent): void;
    _pinch?(e: GestureEvent): void;
    _pinch_end?(e: GestureEvent): void;
    _rotate_start?(e: GestureEvent): void;
    _rotate?(e: GestureEvent): void;
    _rotate_end?(e: GestureEvent): void;
    _tap?(e: TapEvent): void;
    _doubletap?(e: TapEvent): void;
    _press?(e: TapEvent): void;
    _move_enter?(e: MoveEvent): void;
    _move?(e: MoveEvent): void;
    _move_exit?(e: MoveEvent): void;
    _scroll?(e: ScrollEvent): void;
    _keydown?(e: KeyEvent): void;
    _keyup?(e: KeyEvent): void;
}
export declare namespace Tool {
    interface Attrs extends Model.Attrs {
        active: boolean;
    }
    interface Props extends Model.Props {
        active: p.Property<boolean>;
    }
}
export interface Tool extends Tool.Attrs {
}
export declare abstract class Tool extends Model {
    properties: Tool.Props;
    constructor(attrs?: Partial<Tool.Attrs>);
    static initClass(): void;
    readonly event_type?: EventType | EventType[];
    readonly synthetic_renderers: Renderer[];
    protected _get_dim_tooltip(name: string, dims: Dimensions): string;
    _get_dim_limits([sx0, sy0]: [number, number], [sx1, sy1]: [number, number], frame: CartesianFrame, dims: Dimensions): [[number, number], [number, number]];
}
