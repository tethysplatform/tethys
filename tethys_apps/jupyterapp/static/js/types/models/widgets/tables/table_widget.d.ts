import { Widget } from "../widget";
import { ColumnarDataSource } from "../../sources/columnar_data_source";
import { CDSView } from "../../sources/cds_view";
export declare namespace TableWidget {
    interface Attrs extends Widget.Attrs {
        source: ColumnarDataSource;
        view: CDSView;
    }
    interface Props extends Widget.Props {
    }
}
export interface TableWidget extends TableWidget.Attrs {
}
export declare class TableWidget extends Widget {
    properties: TableWidget.Props;
    constructor(attrs?: Partial<TableWidget.Attrs>);
    static initClass(): void;
    initialize(): void;
}
