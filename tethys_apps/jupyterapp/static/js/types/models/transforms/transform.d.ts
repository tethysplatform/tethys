import { Model } from "../../model";
import { Arrayable } from "core/types";
export declare namespace Transform {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface Transform<To = number> extends Transform.Attrs {
}
export declare abstract class Transform<To = number> extends Model {
    properties: Transform.Props;
    constructor(attrs?: Partial<Transform.Attrs>);
    static initClass(): void;
    abstract compute(x: number): To;
    abstract v_compute(xs: Arrayable<number>): Arrayable<To>;
}
