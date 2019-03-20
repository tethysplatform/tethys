import { DataRange } from "./data_range";
import { Renderer } from "../renderers/renderer";
import { PaddingUnits, StartEnd } from "core/enums";
import { Rect } from "core/util/spatial";
export declare type Dim = 0 | 1;
export declare type Bounds = {
    [key: string]: Rect;
};
export declare namespace DataRange1d {
    interface Attrs extends DataRange.Attrs {
        start: number;
        end: number;
        range_padding: number;
        range_padding_units: PaddingUnits;
        flipped: boolean;
        follow: StartEnd;
        follow_interval: number;
        default_span: number;
        scale_hint: "log" | "auto";
    }
    interface Props extends DataRange.Props {
    }
}
export interface DataRange1d extends DataRange1d.Attrs {
}
export declare class DataRange1d extends DataRange {
    properties: DataRange1d.Props;
    constructor(attrs?: Partial<DataRange1d.Attrs>);
    static initClass(): void;
    protected _initial_start: number;
    protected _initial_end: number;
    protected _initial_range_padding: number;
    protected _initial_range_padding_units: PaddingUnits;
    protected _initial_follow: StartEnd;
    protected _initial_follow_interval: number;
    protected _initial_default_span: number;
    protected _plot_bounds: Bounds;
    have_updated_interactively: boolean;
    initialize(): void;
    readonly min: number;
    readonly max: number;
    computed_renderers(): Renderer[];
    protected _compute_plot_bounds(renderers: Renderer[], bounds: Bounds): Rect;
    adjust_bounds_for_aspect(bounds: Rect, ratio: number): Rect;
    protected _compute_min_max(plot_bounds: Bounds, dimension: Dim): [number, number];
    protected _compute_range(min: number, max: number): [number, number];
    update(bounds: Bounds, dimension: Dim, bounds_id: string, ratio?: number): void;
    reset(): void;
}
