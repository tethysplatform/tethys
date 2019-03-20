import { TickSpec } from "./ticker";
import { BasicTicker } from "./basic_ticker";
import { LatLon } from "core/enums";
export declare namespace MercatorTicker {
    interface Attrs extends BasicTicker.Attrs {
        dimension: LatLon | null | undefined;
    }
    interface Props extends BasicTicker.Props {
    }
}
export interface MercatorTicker extends MercatorTicker.Attrs {
}
export declare class MercatorTicker extends BasicTicker {
    properties: MercatorTicker.Props;
    constructor(attrs?: Partial<MercatorTicker.Attrs>);
    static initClass(): void;
    get_ticks_no_defaults(data_low: number, data_high: number, cross_loc: any, desired_n_ticks: number): TickSpec<number>;
}
