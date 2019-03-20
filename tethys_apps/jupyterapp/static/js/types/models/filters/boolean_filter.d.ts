import { Filter } from "./filter";
import { ColumnarDataSource } from "../sources/columnar_data_source";
export declare namespace BooleanFilter {
    interface Attrs extends Filter.Attrs {
        booleans: boolean[] | null;
    }
    interface Props extends Filter.Props {
    }
}
export interface BooleanFilter extends BooleanFilter.Attrs {
}
export declare class BooleanFilter extends Filter {
    properties: BooleanFilter.Props;
    constructor(attrs?: Partial<BooleanFilter.Attrs>);
    static initClass(): void;
    compute_indices(source: ColumnarDataSource): number[] | null;
}
