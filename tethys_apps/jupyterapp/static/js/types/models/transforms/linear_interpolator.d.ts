import { Interpolator } from "./interpolator";
export declare namespace LinearInterpolator {
    interface Attrs extends Interpolator.Attrs {
    }
    interface Props extends Interpolator.Props {
    }
}
export interface LinearInterpolator extends LinearInterpolator.Attrs {
}
export declare class LinearInterpolator extends Interpolator {
    properties: LinearInterpolator.Props;
    constructor(attrs?: Partial<LinearInterpolator.Attrs>);
    static initClass(): void;
    compute(x: number): number;
}
