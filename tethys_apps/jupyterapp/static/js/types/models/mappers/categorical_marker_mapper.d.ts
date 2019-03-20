import { CategoricalMapper } from "./categorical_mapper";
import { Factor } from "../ranges/factor_range";
import { Mapper } from "./mapper";
import { Arrayable } from "core/types";
export declare namespace CategoricalMarkerMapper {
    interface Attrs extends Mapper.Attrs, CategoricalMapper.Attrs {
    }
    interface Props extends Mapper.Props {
    }
}
export interface CategoricalMarkerMapper extends Mapper.Attrs, CategoricalMapper.Attrs {
    markers: string[];
    default_value: string;
}
export declare class CategoricalMarkerMapper extends Mapper<string> {
    properties: CategoricalMarkerMapper.Props;
    constructor(attrs?: Partial<CategoricalMarkerMapper.Attrs>);
    static initClass(): void;
    v_compute(xs: Arrayable<Factor>): Arrayable<string>;
}
