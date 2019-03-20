import { Ticker, TickSpec } from "./ticker";
import { FactorRange, Factor } from "../ranges/factor_range";
export interface FactorTickSpec extends TickSpec<Factor> {
    tops: Factor[];
    mids: Factor[];
}
export declare namespace CategoricalTicker {
    interface Attrs extends Ticker.Attrs {
    }
    interface Props extends Ticker.Props {
    }
}
export interface CategoricalTicker extends CategoricalTicker.Attrs {
}
export declare class CategoricalTicker extends Ticker<Factor> {
    properties: CategoricalTicker.Props;
    constructor(attrs?: Partial<CategoricalTicker.Attrs>);
    static initClass(): void;
    get_ticks(start: number, end: number, range: FactorRange, _cross_loc: any, _: any): FactorTickSpec;
    private _collect;
}
