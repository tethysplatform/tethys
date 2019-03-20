import { AbstractSlider, AbstractSliderView, SliderSpec } from "./abstract_slider";
export declare class DateRangeSliderView extends AbstractSliderView {
    model: DateRangeSlider;
    protected _calc_to(): SliderSpec;
    protected _calc_from(values: number[]): number[];
}
export declare namespace DateRangeSlider {
    interface Attrs extends AbstractSlider.Attrs {
    }
    interface Props extends AbstractSlider.Props {
    }
}
export interface DateRangeSlider extends DateRangeSlider.Attrs {
}
export declare class DateRangeSlider extends AbstractSlider {
    properties: DateRangeSlider.Props;
    constructor(attrs?: Partial<DateRangeSlider.Attrs>);
    static initClass(): void;
    behaviour: "drag";
    connected: boolean[];
    protected _formatter(value: number, format: string): string;
}
