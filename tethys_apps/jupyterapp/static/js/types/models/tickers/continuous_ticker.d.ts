import { Ticker, TickSpec } from "./ticker";
export declare namespace ContinuousTicker {
    interface Attrs extends Ticker.Attrs {
        num_minor_ticks: number;
        desired_num_ticks: number;
    }
    interface Props extends Ticker.Props {
    }
}
export interface ContinuousTicker extends ContinuousTicker.Attrs {
}
export declare abstract class ContinuousTicker extends Ticker<number> {
    properties: ContinuousTicker.Props;
    constructor(attrs?: Partial<ContinuousTicker.Attrs>);
    static initClass(): void;
    min_interval: number;
    max_interval: number;
    get_ticks(data_low: number, data_high: number, _range: any, cross_loc: any, _: any): TickSpec<number>;
    abstract get_interval(data_low: number, data_high: number, desired_n_ticks: number): number;
    get_ticks_no_defaults(data_low: number, data_high: number, _cross_loc: any, desired_n_ticks: number): TickSpec<number>;
    get_min_interval(): number;
    get_max_interval(): number;
    get_ideal_interval(data_low: number, data_high: number, desired_n_ticks: number): number;
}
