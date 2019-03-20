import { LinearAxis, LinearAxisView } from "./linear_axis";
export declare class DatetimeAxisView extends LinearAxisView {
    model: DatetimeAxis;
}
export declare namespace DatetimeAxis {
    interface Attrs extends LinearAxis.Attrs {
    }
    interface Props extends LinearAxis.Props {
    }
}
export interface DatetimeAxis extends DatetimeAxis.Attrs {
}
export declare class DatetimeAxis extends LinearAxis {
    properties: DatetimeAxis.Props;
    constructor(attrs?: Partial<DatetimeAxis.Attrs>);
    static initClass(): void;
}
