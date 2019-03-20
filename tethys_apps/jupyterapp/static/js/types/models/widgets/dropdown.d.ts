import { AbstractButton, AbstractButtonView } from "./abstract_button";
export declare class DropdownView extends AbstractButtonView {
    model: Dropdown;
    connect_signals(): void;
    render(): void;
    protected _clear_menu(): void;
    protected _toggle_menu(): void;
    protected _button_click(event: MouseEvent): void;
    protected _caret_click(event: MouseEvent): void;
    protected _item_click(event: MouseEvent): void;
    set_value(value: string): void;
}
export declare namespace Dropdown {
    interface Attrs extends AbstractButton.Attrs {
        value: string;
        default_value: string;
        menu: ([string, string] | null)[];
    }
    interface Props extends AbstractButton.Props {
    }
}
export interface Dropdown extends Dropdown.Attrs {
    active: boolean;
}
export declare class Dropdown extends AbstractButton {
    properties: Dropdown.Props;
    constructor(attrs?: Partial<Dropdown.Attrs>);
    static initClass(): void;
    readonly is_split_button: boolean;
}
