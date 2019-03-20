import { Interpolator } from "./interpolator";
import { StepMode } from "core/enums";
export declare namespace StepInterpolator {
    interface Attrs extends Interpolator.Attrs {
        mode: StepMode;
    }
    interface Props extends Interpolator.Props {
    }
}
export interface StepInterpolator extends StepInterpolator.Attrs {
}
export declare class StepInterpolator extends Interpolator {
    properties: StepInterpolator.Props;
    constructor(attrs?: Partial<StepInterpolator.Attrs>);
    static initClass(): void;
    compute(x: number): number;
}
