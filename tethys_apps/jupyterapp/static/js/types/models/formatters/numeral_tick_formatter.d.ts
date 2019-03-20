import { TickFormatter } from "./tick_formatter";
import { Axis } from "../axes/axis";
import { RoundingFunction } from "core/enums";
export declare namespace NumeralTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
        format: string;
        language: string;
        rounding: RoundingFunction;
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface NumeralTickFormatter extends NumeralTickFormatter.Attrs {
}
export declare class NumeralTickFormatter extends TickFormatter {
    properties: NumeralTickFormatter.Props;
    constructor(attrs?: Partial<NumeralTickFormatter.Attrs>);
    static initClass(): void;
    private readonly _rounding_fn;
    doFormat(ticks: number[], _axis: Axis): string[];
}
