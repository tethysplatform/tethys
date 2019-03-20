import { ColumnDataSource } from "./column_data_source";
import { Arrayable } from "core/types";
export declare namespace RemoteDataSource {
    interface Attrs extends ColumnDataSource.Attrs {
        data_url: string;
        polling_interval: number;
    }
    interface Props extends ColumnDataSource.Props {
    }
}
export interface RemoteDataSource extends RemoteDataSource.Attrs {
}
export declare abstract class RemoteDataSource extends ColumnDataSource {
    properties: RemoteDataSource.Props;
    constructor(attrs?: Partial<RemoteDataSource.Attrs>);
    get_column(colname: string): Arrayable;
    abstract setup(): void;
    initialize(): void;
    static initClass(): void;
}
