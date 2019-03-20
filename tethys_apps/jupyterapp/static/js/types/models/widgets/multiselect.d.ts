import * as p from "core/properties";
import { InputWidget, InputWidgetView } from "./input_widget";
export declare class MultiSelectView extends InputWidgetView {
    model: MultiSelect;
    protected selectEl: HTMLSelectElement;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    render_selection(): void;
    change_input(): void;
}
export declare namespace MultiSelect {
    interface Attrs extends InputWidget.Attrs {
        value: string[];
        options: (string | [string, string])[];
        size: number;
    }
    interface Props extends InputWidget.Props {
        value: p.Property<string[]>;
        options: p.Property<(string | [string, string])[]>;
        size: p.Property<number>;
    }
}
export interface MultiSelect extends MultiSelect.Attrs {
}
export declare class MultiSelect extends InputWidget {
    properties: MultiSelect.Props;
    constructor(attrs?: Partial<MultiSelect.Attrs>);
    static initClass(): void;
}
