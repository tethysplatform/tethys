import { Transform } from "../transforms/transform";
import { Factor } from "../ranges/factor_range";
import { Arrayable } from "core/types";
export declare namespace Mapper {
    interface Attrs extends Transform.Attrs {
    }
    interface Props extends Transform.Props {
    }
}
export interface Mapper<T> extends Mapper.Attrs {
}
export declare abstract class Mapper<T> extends Transform<T> {
    properties: Mapper.Props;
    constructor(attrs?: Partial<Mapper.Attrs>);
    static initClass(): void;
    compute(_x: number): never;
    abstract v_compute(xs: Arrayable<number> | Arrayable<Factor>): Arrayable<T>;
}
