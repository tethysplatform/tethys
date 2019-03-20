import { TableWidget } from "./table_widget";
import { Column, TableColumn } from "./table_column";
import { WidgetView } from "../widget";
import { ColumnarDataSource } from "../../sources/columnar_data_source";
import { CDSView } from "../../sources/cds_view";
export declare const DTINDEX_NAME = "__bkdt_internal_index__";
export declare type Item = {
    [key: string]: any;
};
export declare class DataProvider {
    readonly source: ColumnarDataSource;
    readonly view: CDSView;
    readonly index: number[];
    constructor(source: ColumnarDataSource, view: CDSView);
    getLength(): number;
    getItem(offset: number): Item;
    setItem(offset: number, item: Item): void;
    getField(offset: number, field: string): any;
    setField(offset: number, field: string, value: any): void;
    getItemMetadata(_index: number): any;
    getRecords(): Item[];
    sort(columns: any[]): void;
    protected _update_source_inplace(): void;
}
export declare class DataTableView extends WidgetView {
    model: DataTable;
    private data;
    private grid;
    protected _in_selection_update: boolean;
    protected _warned_not_reorderable: boolean;
    connect_signals(): void;
    updateGrid(from_source_change?: boolean): void;
    updateSelection(): void;
    newIndexColumn(): Column;
    css_classes(): string[];
    render(): void;
    _hide_header(): void;
}
export declare namespace DataTable {
    interface Attrs extends TableWidget.Attrs {
        columns: TableColumn[];
        fit_columns: boolean;
        sortable: boolean;
        reorderable: boolean;
        editable: boolean;
        selectable: boolean | "checkbox";
        index_position: number | null;
        index_header: string;
        index_width: number;
        scroll_to_selection: boolean;
        header_row: boolean;
    }
    interface Props extends TableWidget.Props {
    }
}
export interface DataTable extends DataTable.Attrs {
}
export declare class DataTable extends TableWidget {
    properties: DataTable.Props;
    constructor(attrs?: Partial<DataTable.Attrs>);
    static initClass(): void;
    readonly default_width: number;
    get_scroll_index(grid_range: {
        top: number;
        bottom: number;
    }, selected_indices: number[]): number | null;
}
