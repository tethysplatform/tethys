import { InputWidget, InputWidgetView } from "./input_widget";
import * as Pikaday from "pikaday";
export declare class DatePickerView extends InputWidgetView {
    model: DatePicker;
    labelEl: HTMLElement;
    inputEl: HTMLElement;
    protected _picker: Pikaday;
    css_classes(): string[];
    render(): void;
    _on_select(date: Date): void;
}
export declare namespace DatePicker {
    interface Attrs extends InputWidget.Attrs {
        value: string;
        min_date: string;
        max_date: string;
    }
    interface Props extends InputWidget.Props {
    }
}
export interface DatePicker extends DatePicker.Attrs {
}
export declare class DatePicker extends InputWidget {
    properties: DatePicker.Props;
    constructor(attrs?: Partial<DatePicker.Attrs>);
    static initClass(): void;
}
