import { AbstractButton, AbstractButtonView } from "./abstract_button";
export declare class ToggleView extends AbstractButtonView {
    model: Toggle;
    render(): void;
    change_input(): void;
}
export declare namespace Toggle {
    interface Attrs extends AbstractButton.Attrs {
        active: boolean;
    }
    interface Props extends AbstractButton.Props {
    }
}
export interface Toggle extends Toggle.Attrs {
}
export declare class Toggle extends AbstractButton {
    properties: Toggle.Props;
    constructor(attrs?: Partial<Toggle.Attrs>);
    static initClass(): void;
}
