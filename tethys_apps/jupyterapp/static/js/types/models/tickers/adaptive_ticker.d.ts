import { ContinuousTicker } from "./continuous_ticker";
export declare namespace AdaptiveTicker {
    interface Attrs extends ContinuousTicker.Attrs {
        base: number;
        mantissas: number[];
        min_interval: number;
        max_interval: number;
    }
    interface Props extends ContinuousTicker.Props {
    }
}
export interface AdaptiveTicker extends AdaptiveTicker.Attrs {
}
export declare class AdaptiveTicker extends ContinuousTicker {
    properties: AdaptiveTicker.Props;
    constructor(attrs?: Partial<AdaptiveTicker.Attrs>);
    static initClass(): void;
    extended_mantissas: number[];
    base_factor: number;
    initialize(): void;
    get_interval(data_low: number, data_high: number, desired_n_ticks: number): number;
}
