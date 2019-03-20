import { Scale } from "./scale";
import { Arrayable } from "core/types";
export declare namespace LinearScale {
    interface Attrs extends Scale.Attrs {
    }
    interface Props extends Scale.Props {
    }
}
export interface LinearScale extends LinearScale.Attrs {
}
export declare class LinearScale extends Scale {
    properties: LinearScale.Props;
    constructor(attrs?: Partial<LinearScale.Attrs>);
    static initClass(): void;
    compute(x: number): number;
    v_compute(xs: Arrayable<number>): Arrayable<number>;
    invert(xprime: number): number;
    v_invert(xprimes: Arrayable<number>): Arrayable<number>;
    protected _compute_state(): [number, number];
}
