import { TickFormatter } from "./tick_formatter";
import { Axis } from "../axes/axis";
export declare namespace DatetimeTickFormatter {
    interface Attrs extends TickFormatter.Attrs {
        microseconds: string[];
        milliseconds: string[];
        seconds: string[];
        minsec: string[];
        minutes: string[];
        hourmin: string[];
        hours: string[];
        days: string[];
        months: string[];
        years: string[];
    }
    interface Props extends TickFormatter.Props {
    }
}
export interface DatetimeTickFormatter extends DatetimeTickFormatter.Attrs {
}
export declare class DatetimeTickFormatter extends TickFormatter {
    properties: DatetimeTickFormatter.Props;
    constructor(attrs?: Partial<DatetimeTickFormatter.Attrs>);
    static initClass(): void;
    protected strip_leading_zeros: boolean;
    protected _width_formats: {
        [key: string]: [number[], string[]];
    };
    initialize(): void;
    protected _update_width_formats(): void;
    protected _get_resolution_str(resolution_secs: number, span_secs: number): string;
    doFormat(ticks: number[], _axis: Axis): string[];
}
