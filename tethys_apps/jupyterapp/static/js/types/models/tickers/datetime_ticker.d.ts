import { CompositeTicker } from "./composite_ticker";
export declare namespace DatetimeTicker {
    interface Attrs extends CompositeTicker.Attrs {
    }
    interface Props extends CompositeTicker.Props {
    }
}
export interface DatetimeTicker extends DatetimeTicker.Attrs {
}
export declare class DatetimeTicker extends CompositeTicker {
    properties: DatetimeTicker.Props;
    constructor(attrs?: Partial<DatetimeTicker.Attrs>);
    static initClass(): void;
}
