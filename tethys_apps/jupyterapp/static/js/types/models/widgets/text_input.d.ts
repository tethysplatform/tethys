import { InputWidget, InputWidgetView } from "./input_widget";
export declare class TextInputView extends InputWidgetView {
    model: TextInput;
    protected inputEl: HTMLInputElement;
    initialize(options: any): void;
    connect_signals(): void;
    css_classes(): string[];
    render(): void;
    change_input(): void;
}
export declare namespace TextInput {
    interface Attrs extends InputWidget.Attrs {
        value: string;
        placeholder: string;
    }
    interface Props extends InputWidget.Props {
    }
}
export interface TextInput extends TextInput.Attrs {
}
export declare class TextInput extends InputWidget {
    properties: TextInput.Props;
    constructor(attrs?: Partial<TextInput.Attrs>);
    static initClass(): void;
}
