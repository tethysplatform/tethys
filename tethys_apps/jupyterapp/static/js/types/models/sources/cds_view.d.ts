import { Model } from "../../model";
import * as p from "core/properties";
import { Selection } from "../selections/selection";
import { Filter } from "../filters/filter";
import { ColumnarDataSource } from "./columnar_data_source";
export declare namespace CDSView {
    interface Attrs extends Model.Attrs {
        filters: Filter[];
        source: ColumnarDataSource;
        indices: number[];
        indices_map: {
            [key: string]: number;
        };
    }
    interface Props extends Model.Props {
        filters: p.Property<Filter[]>;
        source: p.Property<ColumnarDataSource>;
        indices: p.Property<number[]>;
        indices_map: p.Property<{
            [key: string]: number;
        }>;
    }
}
export interface CDSView extends CDSView.Attrs {
}
export declare class CDSView extends Model {
    properties: CDSView.Props;
    constructor(attrs?: Partial<CDSView.Attrs>);
    static initClass(): void;
    initialize(): void;
    connect_signals(): void;
    compute_indices(): void;
    indices_map_to_subset(): void;
    convert_selection_from_subset(selection_subset: Selection): Selection;
    convert_selection_to_subset(selection_full: Selection): Selection;
    convert_indices_from_subset(indices: number[]): number[];
}
