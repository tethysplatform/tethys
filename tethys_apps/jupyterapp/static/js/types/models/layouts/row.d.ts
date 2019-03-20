import { Box, BoxView } from "./box";
export declare class RowView extends BoxView {
    model: Row;
    css_classes(): string[];
}
export declare namespace Row {
    interface Attrs extends Box.Attrs {
    }
    interface Props extends Box.Props {
    }
}
export interface Row extends Row.Attrs {
}
export declare class Row extends Box {
    properties: Row.Props;
    constructor(attrs?: Partial<Row.Attrs>);
    static initClass(): void;
    _horizontal: boolean;
}
