import { Mapper } from "./mapper";
import { Arrayable } from "core/types";
import { Factor } from "../ranges/factor_range";
export declare function _cat_equals(a: Arrayable<any>, b: Arrayable<any>): boolean;
export declare function cat_v_compute<T>(data: Arrayable<Factor>, factors: string[], targets: Arrayable<T>, values: Arrayable<T>, start: number, end: number, extra_value: T): void;
export declare namespace CategoricalMapper {
    interface Attrs extends Mapper.Attrs {
        factors: string[];
        start: number;
        end: number;
    }
    interface Props extends Mapper.Props {
    }
}
export interface CategoricalMapper extends CategoricalMapper.Attrs {
}
