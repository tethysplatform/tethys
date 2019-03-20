import { TickFormatter } from "./tick_formatter";
import { BasicTickFormatter } from "./basic_tick_formatter";
import { LogTicker } from "../tickers/log_ticker";
import { Axis } from "../axes/axis";
export declare namespace LogTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
        ticker: LogTicker | null;
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface LogTickFormatter extends LogTickFormatter.Attrs {
}
export declare class LogTickFormatter extends TickFormatter {
    properties: LogTickFormatter.Props;
    constructor(attrs?: Partial<LogTickFormatter.Attrs>);
    static initClass(): void;
    protected basic_formatter: BasicTickFormatter;
    initialize(): void;
    doFormat(ticks: number[], axis: Axis): string[];
}
