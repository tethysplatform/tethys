import { Transform } from "./transform";
import { Range } from "../ranges/range";
import { Factor } from "../ranges/factor_range";
import { Arrayable } from "core/types";
export declare namespace Dodge {
    interface Attrs extends Transform.Attrs {
        value: number;
        range: Range;
    }
    interface Props extends Transform.Props {
    }
}
export interface Dodge extends Dodge.Attrs {
}
export declare class Dodge extends Transform {
    properties: Dodge.Props;
    constructor(attrs?: Partial<Dodge.Attrs>);
    static initClass(): void;
    v_compute(xs0: Arrayable<number | Factor>): Arrayable<number>;
    compute(x: number | Factor): number;
    protected _compute(x: number): number;
}
