import { TickSpec } from "./ticker";
import { SingleIntervalTicker } from "./single_interval_ticker";
export declare namespace DaysTicker {
    interface Attrs extends SingleIntervalTicker.Attrs {
        days: number[];
    }
    interface Props extends SingleIntervalTicker.Props {
    }
}
export interface DaysTicker extends DaysTicker.Attrs {
}
export declare class DaysTicker extends SingleIntervalTicker {
    properties: DaysTicker.Props;
    constructor(attrs?: Partial<DaysTicker.Attrs>);
    static initClass(): void;
    initialize(): void;
    get_ticks_no_defaults(data_low: number, data_high: number, _cross_loc: any, _desired_n_ticks: number): TickSpec<number>;
}
