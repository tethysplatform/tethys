import { TextInput, TextInputView } from "./text_input";
export declare class AutocompleteInputView extends TextInputView {
    model: AutocompleteInput;
    protected menuEl: HTMLElement;
    connect_signals(): void;
    render(): void;
    protected _render_items(completions: string[]): void;
    protected _open_menu(): void;
    protected _clear_menu(): void;
    protected _item_click(event: MouseEvent): void;
    _keydown(_event: KeyboardEvent): void;
    _keyup(event: KeyboardEvent): void;
}
export declare namespace AutocompleteInput {
    interface Attrs extends TextInput.Attrs {
        completions: string[];
    }
    interface Props extends TextInput.Props {
    }
}
export interface AutocompleteInput extends AutocompleteInput.Attrs {
}
export declare class AutocompleteInput extends TextInput {
    properties: AutocompleteInput.Props;
    constructor(attrs?: Partial<AutocompleteInput.Attrs>);
    static initClass(): void;
    active: boolean;
}
