import { TickFormatter } from "./tick_formatter";
import { Axis } from "../axes/axis";
export declare namespace CategoricalTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface CategoricalTickFormatter extends CategoricalTickFormatter.Attrs {
}
export declare class CategoricalTickFormatter extends TickFormatter {
    properties: CategoricalTickFormatter.Props;
    constructor(attrs?: Partial<CategoricalTickFormatter.Attrs>);
    static initClass(): void;
    doFormat(ticks: string[], _axis: Axis): string[];
}
