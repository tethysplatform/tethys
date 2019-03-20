import { Model } from "../../model";
import { DataSource } from "../sources/data_source";
export declare namespace Filter {
    interface Attrs extends Model.Attrs {
        filter: boolean[] | number[] | null;
    }
    interface Props extends Model.Props {
    }
}
export interface Filter extends Filter.Attrs {
}
export declare class Filter extends Model {
    properties: Filter.Props;
    constructor(attrs?: Partial<Filter.Attrs>);
    static initClass(): void;
    compute_indices(_source: DataSource): number[] | null;
}
