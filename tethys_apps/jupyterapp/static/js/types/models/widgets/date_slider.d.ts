import { AbstractSlider, AbstractSliderView, SliderSpec } from "./abstract_slider";
export declare class DateSliderView extends AbstractSliderView {
    model: DateSlider;
    protected _calc_to(): SliderSpec;
    protected _calc_from([value]: number[]): number;
}
export declare namespace DateSlider {
    interface Attrs extends AbstractSlider.Attrs {
    }
    interface Props extends AbstractSlider.Props {
    }
}
export interface DateSlider extends DateSlider.Attrs {
}
export declare class DateSlider extends AbstractSlider {
    properties: DateSlider.Props;
    constructor(attrs?: Partial<DateSlider.Attrs>);
    static initClass(): void;
    behaviour: "tap";
    connected: boolean[];
    protected _formatter(value: number, format: string): string;
}
