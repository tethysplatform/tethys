import { ColumnarDataSource } from "./columnar_data_source";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import { Set } from "core/util/data_structures";
import { Shape } from "core/util/serialization";
export declare function stream_to_column(col: Arrayable, new_col: Arrayable, rollover?: number): Arrayable;
export declare function slice(ind: number | {
    start?: number;
    stop?: number;
    step?: number;
}, length: number): [number, number, number];
export declare type Index = number | [number, number] | [number, number, number];
export declare function patch_to_column(col: Arrayable, patch: [Index, any][], shapes: Shape[]): Set<number>;
export declare namespace ColumnDataSource {
    interface Attrs extends ColumnarDataSource.Attrs {
        data: {
            [key: string]: Arrayable;
        };
    }
    interface Props extends ColumnarDataSource.Props {
        data: p.Property<{
            [key: string]: Arrayable;
        }>;
    }
}
export interface ColumnDataSource extends ColumnDataSource.Attrs {
}
export declare class ColumnDataSource extends ColumnarDataSource {
    properties: ColumnDataSource.Props;
    constructor(attrs?: Partial<ColumnDataSource.Attrs>);
    static initClass(): void;
    initialize(): void;
    attributes_as_json(include_defaults?: boolean, value_to_json?: typeof ColumnDataSource._value_to_json): any;
    static _value_to_json(key: string, value: any, optional_parent_object: any): any;
    stream(new_data: {
        [key: string]: any[];
    }, rollover?: number): void;
    patch(patches: {
        [key: string]: [Index, any][];
    }): void;
}
