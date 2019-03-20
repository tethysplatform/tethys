import { AbstractSlider, AbstractSliderView, SliderSpec } from "./abstract_slider";
export declare class RangeSliderView extends AbstractSliderView {
    model: RangeSlider;
    protected _calc_to(): SliderSpec;
    protected _calc_from(values: number[]): number[];
}
export declare namespace RangeSlider {
    interface Attrs extends AbstractSlider.Attrs {
    }
    interface Props extends AbstractSlider.Props {
    }
}
export interface RangeSlider extends RangeSlider.Attrs {
}
export declare class RangeSlider extends AbstractSlider {
    properties: RangeSlider.Props;
    constructor(attrs?: Partial<RangeSlider.Attrs>);
    static initClass(): void;
    behaviour: "drag";
    connected: boolean[];
    protected _formatter(value: number, format: string): string;
}
