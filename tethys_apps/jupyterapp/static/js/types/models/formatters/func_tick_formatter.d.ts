import { TickFormatter } from "./tick_formatter";
import { Axis } from "../axes/axis";
export declare namespace FuncTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
        args: {
            [key: string]: any;
        };
        code: string;
        use_strict: boolean;
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface FuncTickFormatter extends FuncTickFormatter.Attrs {
}
export declare class FuncTickFormatter extends TickFormatter {
    properties: FuncTickFormatter.Props;
    constructor(attrs?: Partial<FuncTickFormatter.Attrs>);
    static initClass(): void;
    readonly names: string[];
    readonly values: any[];
    protected _make_func(): Function;
    doFormat(ticks: number[], _axis: Axis): string[];
}
