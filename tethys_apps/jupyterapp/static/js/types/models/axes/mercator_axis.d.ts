import { AxisView } from "./axis";
import { LinearAxis } from "./linear_axis";
import { MercatorTickFormatter } from "../formatters/mercator_tick_formatter";
import { MercatorTicker } from "../tickers/mercator_ticker";
export declare class MercatorAxisView extends AxisView {
    model: MercatorAxis;
}
export declare namespace MercatorAxis {
    interface Attrs extends LinearAxis.Attrs {
        ticker: MercatorTicker;
        formatter: MercatorTickFormatter;
    }
    interface Props extends LinearAxis.Props {
    }
}
export interface MercatorAxis extends MercatorAxis.Attrs {
}
export declare class MercatorAxis extends LinearAxis {
    properties: MercatorAxis.Props;
    ticker: MercatorTicker;
    formatter: MercatorTickFormatter;
    constructor(attrs?: Partial<MercatorAxis.Attrs>);
    static initClass(): void;
}
