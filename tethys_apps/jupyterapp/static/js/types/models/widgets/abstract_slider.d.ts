import * as noUiSlider from "nouislider";
import { Color } from "core/types";
import { Orientation, SliderCallbackPolicy } from "core/enums";
import { Widget, WidgetView } from "./widget";
export interface SliderSpec {
    start: number;
    end: number;
    value: number[];
    step: number;
}
export declare abstract class AbstractSliderView extends WidgetView {
    model: AbstractSlider;
    protected sliderEl: noUiSlider.Instance;
    protected titleEl: HTMLElement;
    protected valueEl: HTMLElement;
    protected callback_wrapper?: () => void;
    initialize(options: any): void;
    connect_signals(): void;
    protected abstract _calc_to(): SliderSpec;
    protected abstract _calc_from(values: number[]): number | number[];
    render(): void;
    protected _slide(values: number[]): void;
    protected _change(values: number[]): void;
}
export declare namespace AbstractSlider {
    interface Attrs extends Widget.Attrs {
        title: string;
        show_value: boolean;
        start: any;
        end: any;
        value: any;
        step: number;
        format: string;
        orientation: Orientation;
        direction: "ltr" | "rtl";
        tooltips: boolean;
        callback: any;
        callback_throttle: number;
        callback_policy: SliderCallbackPolicy;
        bar_color: Color;
    }
    interface Props extends Widget.Props {
    }
}
export interface AbstractSlider extends AbstractSlider.Attrs {
}
export declare abstract class AbstractSlider extends Widget {
    properties: AbstractSlider.Props;
    constructor(attrs?: Partial<AbstractSlider.Attrs>);
    static initClass(): void;
    behaviour: "drag" | "tap";
    connected: false | boolean[];
    protected _formatter(value: number, _format: string): string;
    pretty(value: number): string;
}
