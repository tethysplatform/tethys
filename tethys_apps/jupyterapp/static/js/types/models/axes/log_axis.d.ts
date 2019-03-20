import { AxisView } from "./axis";
import { ContinuousAxis } from "./continuous_axis";
import { LogTickFormatter } from "../formatters/log_tick_formatter";
import { LogTicker } from "../tickers/log_ticker";
export declare class LogAxisView extends AxisView {
    model: LogAxis;
}
export declare namespace LogAxis {
    interface Attrs extends ContinuousAxis.Attrs {
        ticker: LogTicker;
        formatter: LogTickFormatter;
    }
    interface Props extends ContinuousAxis.Props {
    }
}
export interface LogAxis extends LogAxis.Attrs {
}
export declare class LogAxis extends ContinuousAxis {
    properties: LogAxis.Props;
    ticker: LogTicker;
    formatter: LogTickFormatter;
    constructor(attrs?: Partial<LogAxis.Attrs>);
    static initClass(): void;
}
