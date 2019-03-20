import { TickFormatter } from "./tick_formatter";
import { Axis } from "../axes/axis";
export declare namespace BasicTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
        precision: number | "auto";
        use_scientific: boolean;
        power_limit_high: number;
        power_limit_low: number;
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface BasicTickFormatter extends BasicTickFormatter.Attrs {
}
export declare class BasicTickFormatter extends TickFormatter {
    properties: BasicTickFormatter.Props;
    constructor(attrs?: Partial<BasicTickFormatter.Attrs>);
    static initClass(): void;
    protected last_precision: number;
    readonly scientific_limit_low: number;
    readonly scientific_limit_high: number;
    doFormat(ticks: number[], _axis: Axis): string[];
}
