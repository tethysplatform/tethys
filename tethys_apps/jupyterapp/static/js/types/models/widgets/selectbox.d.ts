import { InputWidget, InputWidgetView } from "./input_widget";
export declare class SelectView extends InputWidgetView {
    model: Select;
    protected selectEl: HTMLSelectElement;
    initialize(options: any): void;
    connect_signals(): void;
    build_options(values: (string | [string, string])[]): HTMLElement[];
    render(): void;
    change_input(): void;
}
export declare namespace Select {
    interface Attrs extends InputWidget.Attrs {
        value: string;
        options: (string | [string, string])[] | {
            [key: string]: (string | [string, string])[];
        };
    }
    interface Props extends InputWidget.Props {
    }
}
export interface Select extends Select.Attrs {
}
export declare class Select extends InputWidget {
    properties: Select.Props;
    constructor(attrs?: Partial<Select.Attrs>);
    static initClass(): void;
}
