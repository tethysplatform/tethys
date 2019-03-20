import { CellFormatter } from "./cell_formatters";
import { CellEditor } from "./cell_editors";
import { Class } from "core/class";
import { View } from "core/view";
import { Model } from "../../../model";
export declare type Column = {
    id: string;
    field: string;
    name: string;
    width?: number;
    formatter?: (...args: any[]) => HTMLElement;
    model?: CellEditor;
    editor?: Class<View>;
    sortable?: boolean;
    resizable?: boolean;
    selectable?: boolean;
    defaultSortAsc?: boolean;
    behavior?: "select" | "selectAndMove";
    cannotTriggerInsert?: boolean;
    cssClass?: string;
    headerCssClass?: string;
};
export declare namespace TableColumn {
    interface Attrs extends Model.Attrs {
        field: string;
        title: string;
        width: number;
        formatter: CellFormatter;
        editor: CellEditor;
        sortable: boolean;
        default_sort: "ascending" | "descending";
    }
    interface Props extends Model.Props {
    }
}
export interface TableColumn extends TableColumn.Attrs {
}
export declare class TableColumn extends Model {
    properties: TableColumn.Props;
    constructor(attrs?: Partial<TableColumn.Attrs>);
    static initClass(): void;
    toColumn(): Column;
}
