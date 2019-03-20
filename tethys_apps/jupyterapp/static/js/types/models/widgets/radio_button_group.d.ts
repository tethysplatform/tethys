import { Widget, WidgetView } from "./widget";
import { ButtonType } from "./abstract_button";
export declare class RadioButtonGroupView extends WidgetView {
    model: RadioButtonGroup;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    change_input(): void;
}
export declare namespace RadioButtonGroup {
    interface Attrs extends Widget.Attrs {
        active: number;
        labels: string[];
        button_type: ButtonType;
        callback: any;
    }
    interface Props extends Widget.Props {
    }
}
export interface RadioButtonGroup extends RadioButtonGroup.Attrs {
}
export declare class RadioButtonGroup extends Widget {
    properties: RadioButtonGroup.Props;
    constructor(attrs?: Partial<RadioButtonGroup.Attrs>);
    static initClass(): void;
}
