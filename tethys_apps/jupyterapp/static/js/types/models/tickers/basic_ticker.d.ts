import { AdaptiveTicker } from "./adaptive_ticker";
export declare namespace BasicTicker {
    interface Attrs extends AdaptiveTicker.Attrs {
    }
    interface Props extends AdaptiveTicker.Props {
    }
}
export interface BasicTicker extends BasicTicker.Attrs {
}
export declare class BasicTicker extends AdaptiveTicker {
    properties: BasicTicker.Props;
    constructor(attrs?: Partial<BasicTicker.Attrs>);
    static initClass(): void;
}
