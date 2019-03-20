import { TickFormatter } from "./tick_formatter";
import { Axis } from "../axes/axis";
export declare namespace PrintfTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
        format: string;
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface PrintfTickFormatter extends PrintfTickFormatter.Attrs {
}
export declare class PrintfTickFormatter extends TickFormatter {
    properties: PrintfTickFormatter.Props;
    constructor(attrs?: Partial<PrintfTickFormatter.Attrs>);
    static initClass(): void;
    doFormat(ticks: number[], _axis: Axis): string[];
}
