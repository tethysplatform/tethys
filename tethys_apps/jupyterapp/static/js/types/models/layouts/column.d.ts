import { Box, BoxView } from "./box";
export declare class ColumnView extends BoxView {
    model: Column;
    css_classes(): string[];
}
export declare namespace Column {
    interface Attrs extends Box.Attrs {
    }
    interface Props extends Box.Props {
    }
}
export interface Column extends Column.Attrs {
}
export declare class Column extends Box {
    properties: Column.Props;
    constructor(attrs?: Partial<Column.Attrs>);
    static initClass(): void;
    _horizontal: boolean;
}
