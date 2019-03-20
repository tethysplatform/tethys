import { TickSpec } from "./ticker";
import { BasicTicker } from "./basic_ticker";
import { SingleIntervalTicker } from "./single_interval_ticker";
export declare namespace YearsTicker {
    interface Attrs extends SingleIntervalTicker.Attrs {
    }
    interface Props extends SingleIntervalTicker.Props {
    }
}
export interface YearsTicker extends YearsTicker.Attrs {
}
export declare class YearsTicker extends SingleIntervalTicker {
    properties: YearsTicker.Props;
    constructor(attrs?: Partial<YearsTicker.Attrs>);
    static initClass(): void;
    protected basic_ticker: BasicTicker;
    initialize(): void;
    get_ticks_no_defaults(data_low: number, data_high: number, cross_loc: any, desired_n_ticks: number): TickSpec<number>;
}
