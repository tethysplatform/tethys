import { AbstractButton, AbstractButtonView } from "./abstract_button";
export declare class ButtonView extends AbstractButtonView {
    model: Button;
    change_input(): void;
}
export declare namespace Button {
    interface Attrs extends AbstractButton.Attrs {
        clicks: number;
    }
    interface Props extends AbstractButton.Props {
    }
}
export interface Button extends Button.Attrs {
}
export declare class Button extends AbstractButton {
    properties: Button.Props;
    constructor(attrs?: Partial<Button.Attrs>);
    static initClass(): void;
}
