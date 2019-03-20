import { Widget, WidgetView } from "./widget";
import { AbstractIcon, AbstractIconView } from "./abstract_icon";
export declare type ButtonType = "default" | "primary" | "success" | "warning" | "danger" | "link";
export declare abstract class AbstractButtonView extends WidgetView {
    model: AbstractButton;
    protected icon_views: {
        [key: string]: AbstractIconView;
    };
    protected buttonEl: HTMLButtonElement;
    initialize(options: any): void;
    connect_signals(): void;
    remove(): void;
    _render_button(...children: (string | HTMLElement)[]): HTMLButtonElement;
    render(): void;
    protected _button_click(event: Event): void;
    change_input(): void;
}
export declare namespace AbstractButton {
    interface Attrs extends Widget.Attrs {
        label: string;
        icon: AbstractIcon;
        button_type: ButtonType;
        callback: any;
    }
    interface Props extends Widget.Props {
    }
}
export interface AbstractButton extends AbstractButton.Attrs {
}
export declare abstract class AbstractButton extends Widget {
    properties: AbstractButton.Props;
    constructor(attrs?: Partial<AbstractButton.Attrs>);
    static initClass(): void;
}
