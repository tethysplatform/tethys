import { Filter } from "./filter";
import { DataSource } from "../sources/data_source";
export declare namespace IndexFilter {
    interface Attrs extends Filter.Attrs {
        indices: number[] | null;
    }
    interface Props extends Filter.Props {
    }
}
export interface IndexFilter extends IndexFilter.Attrs {
}
export declare class IndexFilter extends Filter {
    properties: IndexFilter.Props;
    constructor(attrs?: Partial<IndexFilter.Attrs>);
    static initClass(): void;
    compute_indices(_source: DataSource): number[] | null;
}
