import { TickSpec } from "./ticker";
import { SingleIntervalTicker } from "./single_interval_ticker";
export declare namespace MonthsTicker {
    interface Attrs extends SingleIntervalTicker.Attrs {
        months: number[];
    }
    interface Props extends SingleIntervalTicker.Props {
    }
}
export interface MonthsTicker extends MonthsTicker.Attrs {
}
export declare class MonthsTicker extends SingleIntervalTicker {
    properties: MonthsTicker.Props;
    constructor(attrs?: Partial<MonthsTicker.Attrs>);
    static initClass(): void;
    initialize(): void;
    get_ticks_no_defaults(data_low: number, data_high: number, _cross_loc: any, _desired_n_ticks: number): TickSpec<number>;
}
