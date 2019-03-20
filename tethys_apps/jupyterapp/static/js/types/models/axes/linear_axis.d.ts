import { AxisView } from "./axis";
import { ContinuousAxis } from "./continuous_axis";
import { BasicTickFormatter } from "../formatters/basic_tick_formatter";
import { BasicTicker } from "../tickers/basic_ticker";
export declare class LinearAxisView extends AxisView {
    model: LinearAxis;
}
export declare namespace LinearAxis {
    interface Attrs extends ContinuousAxis.Attrs {
        ticker: BasicTicker;
        formatters: BasicTickFormatter;
    }
    interface Props extends ContinuousAxis.Props {
    }
}
export interface LinearAxis extends LinearAxis.Attrs {
}
export declare class LinearAxis extends ContinuousAxis {
    properties: LinearAxis.Props;
    ticker: BasicTicker;
    formatters: BasicTickFormatter;
    constructor(attrs?: Partial<LinearAxis.Attrs>);
    static initClass(): void;
}
