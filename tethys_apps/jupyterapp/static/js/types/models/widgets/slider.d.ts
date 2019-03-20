import { AbstractSlider, AbstractSliderView, SliderSpec } from "./abstract_slider";
export declare class SliderView extends AbstractSliderView {
    model: Slider;
    protected _calc_to(): SliderSpec;
    protected _calc_from([value]: number[]): number;
}
export declare namespace Slider {
    interface Attrs extends AbstractSlider.Attrs {
    }
    interface Props extends AbstractSlider.Props {
    }
}
export interface Slider extends Slider.Attrs {
}
export declare class Slider extends AbstractSlider {
    properties: Slider.Props;
    constructor(attrs?: Partial<Slider.Attrs>);
    static initClass(): void;
    behaviour: "tap";
    connected: boolean[];
    protected _formatter(value: number, format: string): string;
}
