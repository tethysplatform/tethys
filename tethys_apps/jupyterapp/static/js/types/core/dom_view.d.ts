import { View, ViewOptions } from "./view";
import { Solver } from "./layout/solver";
export declare class DOMView extends View {
    tagName: keyof HTMLElementTagNameMap;
    protected _has_finished: boolean;
    protected _solver: Solver;
    el: HTMLElement;
    initialize(options: ViewOptions): void;
    remove(): void;
    css_classes(): string[];
    cursor(_sx: number, _sy: number): string | null;
    layout(): void;
    render(): void;
    renderTo(element: HTMLElement): void;
    on_hit?(sx: number, sy: number): boolean;
    has_finished(): boolean;
    protected readonly _root_element: HTMLElement;
    readonly solver: Solver;
    readonly is_idle: boolean;
    protected _createElement(): HTMLElement;
}
