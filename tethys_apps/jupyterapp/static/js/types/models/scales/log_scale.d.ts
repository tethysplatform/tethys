import { Scale } from "./scale";
import { Arrayable } from "core/types";
export declare namespace LogScale {
    interface Attrs extends Scale.Attrs {
    }
    interface Props extends Scale.Props {
    }
}
export interface LogScale extends LogScale.Attrs {
}
export declare class LogScale extends Scale {
    properties: LogScale.Props;
    constructor(attrs?: Partial<LogScale.Attrs>);
    static initClass(): void;
    compute(x: number): number;
    v_compute(xs: Arrayable<number>): Arrayable<number>;
    invert(xprime: number): number;
    v_invert(xprimes: Arrayable<number>): Arrayable<number>;
    protected _get_safe_factor(orig_start: number, orig_end: number): [number, number];
    protected _compute_state(): [number, number, number, number];
}
