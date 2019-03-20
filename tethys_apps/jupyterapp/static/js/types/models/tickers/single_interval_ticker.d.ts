import { ContinuousTicker } from "./continuous_ticker";
export declare namespace SingleIntervalTicker {
    interface Attrs extends ContinuousTicker.Attrs {
        interval: number;
    }
    interface Props extends ContinuousTicker.Props {
    }
}
export interface SingleIntervalTicker extends SingleIntervalTicker.Attrs {
}
export declare class SingleIntervalTicker extends ContinuousTicker {
    properties: SingleIntervalTicker.Props;
    constructor(attrs?: Partial<SingleIntervalTicker.Attrs>);
    static initClass(): void;
    get_interval(_data_low: number, _data_high: number, _n_desired_ticks: number): number;
    readonly min_interval: number;
    readonly max_interval: number;
}
