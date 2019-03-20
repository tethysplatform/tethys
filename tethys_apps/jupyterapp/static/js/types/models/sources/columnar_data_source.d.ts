import { DataSource } from "./data_source";
import { Signal, Signal0 } from "core/signaling";
import { SelectionManager } from "core/selection_manager";
import * as p from "core/properties";
import { Arrayable } from "core/types";
import { Shape } from "core/util/serialization";
import { Selection } from "../selections/selection";
import { SelectionPolicy } from "../selections/interaction_policy";
export declare namespace ColumnarDataSource {
    interface Attrs extends DataSource.Attrs {
        selection_policy: SelectionPolicy;
        selection_manager: SelectionManager;
        inspected: Selection;
        _shapes: {
            [key: string]: Shape | Shape[];
        };
    }
    interface Props extends DataSource.Props {
        data: p.Property<{
            [key: string]: Arrayable;
        }>;
    }
}
export interface ColumnarDataSource extends ColumnarDataSource.Attrs {
}
export declare abstract class ColumnarDataSource extends DataSource {
    properties: ColumnarDataSource.Props;
    data: {
        [key: string]: Arrayable;
    };
    get_array<T>(key: string): T[];
    _select: Signal0<this>;
    inspect: Signal<any, this>;
    streaming: Signal0<this>;
    patching: Signal<number[], this>;
    constructor(attrs?: Partial<ColumnarDataSource.Attrs>);
    static initClass(): void;
    initialize(): void;
    get_column(colname: string): Arrayable | null;
    columns(): string[];
    get_length(soft?: boolean): number | null;
    get_indices(): number[];
    clear(): void;
}
