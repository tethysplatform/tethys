import { LinearScale } from "./linear_scale";
import { FactorRange } from "../ranges/factor_range";
import { Arrayable } from "core/types";
export declare namespace CategoricalScale {
    interface Attrs extends LinearScale.Attrs {
    }
    interface Props extends LinearScale.Props {
    }
}
export interface CategoricalScale extends CategoricalScale.Attrs {
}
export declare class CategoricalScale extends LinearScale {
    properties: CategoricalScale.Props;
    constructor(attrs?: Partial<CategoricalScale.Attrs>);
    static initClass(): void;
    source_range: FactorRange;
    compute(x: any): number;
    v_compute(xs: Arrayable<any>): Arrayable<number>;
}
