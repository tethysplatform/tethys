import { Model } from "../../model";
import * as p from "core/properties";
import { Selection } from "../selections/selection";
export declare namespace DataSource {
    interface Attrs extends Model.Attrs {
        selected: Selection;
        callback: any;
    }
    interface Props extends Model.Props {
        selected: p.Property<Selection>;
        callback: p.Property<any>;
    }
}
export interface DataSource extends DataSource.Attrs {
}
export declare abstract class DataSource extends Model {
    properties: DataSource.Props;
    constructor(attrs?: Partial<DataSource.Attrs>);
    static initClass(): void;
    connect_signals(): void;
    setup?(): void;
}
