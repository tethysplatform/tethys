import { Transform } from "./transform";
import { Range } from "../ranges/range";
import { Factor } from "../ranges/factor_range";
import { Distribution } from "core/enums";
import { Arrayable } from "core/types";
export declare namespace Jitter {
    interface Attrs extends Transform.Attrs {
        mean: number;
        width: number;
        distribution: Distribution;
        range: Range;
        previous_values: Arrayable<number>;
    }
    interface Props extends Transform.Props {
    }
}
export interface Jitter extends Jitter.Attrs {
}
export declare class Jitter extends Transform {
    properties: Jitter.Props;
    constructor(attrs?: Partial<Jitter.Attrs>);
    static initClass(): void;
    v_compute(xs0: Arrayable<number | Factor>): Arrayable<number>;
    compute(x: number | Factor): number;
    protected _compute(x: number): number;
}
