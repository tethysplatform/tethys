import { Filter } from "./filter";
import { ColumnarDataSource } from "../sources/columnar_data_source";
export declare namespace GroupFilter {
    interface Attrs extends Filter.Attrs {
        column_name: string;
        group: string;
    }
    interface Props extends Filter.Props {
    }
}
export interface GroupFilter extends GroupFilter.Attrs {
}
export declare class GroupFilter extends Filter {
    properties: GroupFilter.Props;
    constructor(attrs?: Partial<GroupFilter.Attrs>);
    static initClass(): void;
    indices: number[] | null;
    compute_indices(source: ColumnarDataSource): number[] | null;
}
