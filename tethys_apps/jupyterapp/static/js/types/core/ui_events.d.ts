import { Input } from "hammerjs";
export declare type HammerEvent = typeof Input;
import { Signal } from "./signaling";
import { DOMView } from "./dom_view";
import { Keys } from "./dom";
import { PlotCanvasView } from "../models/plots/plot_canvas";
import { Plot } from "../models/plots/plot";
import { Toolbar } from "../models/tools/toolbar";
import { ToolView } from "../models/tools/tool";
export declare const is_mobile: boolean;
export interface UIEvent {
    type: string;
    sx: number;
    sy: number;
}
export interface GestureEvent extends UIEvent {
    deltaX: number;
    deltaY: number;
    scale: number;
    shiftKey: boolean;
}
export interface TapEvent extends UIEvent {
    shiftKey: boolean;
}
export interface MoveEvent extends UIEvent {
}
export interface ScrollEvent extends UIEvent {
    delta: number;
}
export interface KeyEvent {
    type: string;
    keyCode: Keys;
}
export declare type EventType = "pan" | "pinch" | "rotate" | "move" | "tap" | "press" | "scroll";
export declare type UISignal<E> = Signal<{
    id: string | null;
    e: E;
}, UIEvents>;
export declare class UIEvents implements EventListenerObject {
    readonly plot_view: PlotCanvasView;
    readonly toolbar: Toolbar;
    readonly hit_area: HTMLElement;
    readonly plot: Plot;
    readonly pan_start: UISignal<GestureEvent>;
    readonly pan: UISignal<GestureEvent>;
    readonly pan_end: UISignal<GestureEvent>;
    readonly pinch_start: UISignal<GestureEvent>;
    readonly pinch: UISignal<GestureEvent>;
    readonly pinch_end: UISignal<GestureEvent>;
    readonly rotate_start: UISignal<GestureEvent>;
    readonly rotate: UISignal<GestureEvent>;
    readonly rotate_end: UISignal<GestureEvent>;
    readonly tap: UISignal<TapEvent>;
    readonly doubletap: UISignal<TapEvent>;
    readonly press: UISignal<TapEvent>;
    readonly move_enter: UISignal<MoveEvent>;
    readonly move: UISignal<MoveEvent>;
    readonly move_exit: UISignal<MoveEvent>;
    readonly scroll: UISignal<ScrollEvent>;
    readonly keydown: UISignal<KeyEvent>;
    readonly keyup: UISignal<KeyEvent>;
    protected readonly hammer: HammerManager;
    constructor(plot_view: PlotCanvasView, toolbar: Toolbar, hit_area: HTMLElement, plot: Plot);
    destroy(): void;
    handleEvent(e: KeyboardEvent): void;
    protected _configure_hammerjs(): void;
    register_tool(tool_view: ToolView): void;
    private _register_tool;
    protected _hit_test_renderers(sx: number, sy: number): DOMView | null;
    protected _hit_test_frame(sx: number, sy: number): boolean;
    _trigger<E extends UIEvent>(signal: UISignal<E>, e: E, srcEvent: Event): void;
    trigger<E>(signal: UISignal<E>, e: E, id?: string | null): void;
    protected _trigger_bokeh_event(e: UIEvent): void;
    protected _get_sxy(event: TouchEvent | MouseEvent | PointerEvent): {
        sx: number;
        sy: number;
    };
    protected _gesture_event(e: HammerEvent): GestureEvent;
    protected _tap_event(e: HammerEvent): TapEvent;
    protected _move_event(e: MouseEvent): MoveEvent;
    protected _scroll_event(e: WheelEvent): ScrollEvent;
    protected _key_event(e: KeyboardEvent): KeyEvent;
    protected _pan_start(e: HammerEvent): void;
    protected _pan(e: HammerEvent): void;
    protected _pan_end(e: HammerEvent): void;
    protected _pinch_start(e: HammerEvent): void;
    protected _pinch(e: HammerEvent): void;
    protected _pinch_end(e: HammerEvent): void;
    protected _rotate_start(e: HammerEvent): void;
    protected _rotate(e: HammerEvent): void;
    protected _rotate_end(e: HammerEvent): void;
    protected _tap(e: HammerEvent): void;
    protected _doubletap(e: HammerEvent): void;
    protected _press(e: HammerEvent): void;
    protected _mouse_enter(e: MouseEvent): void;
    protected _mouse_move(e: MouseEvent): void;
    protected _mouse_exit(e: MouseEvent): void;
    protected _mouse_wheel(e: WheelEvent): void;
    protected _key_down(e: KeyboardEvent): void;
    protected _key_up(e: KeyboardEvent): void;
}
