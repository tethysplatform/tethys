import { Widget, WidgetView } from "./widget";
import { ButtonType } from "./abstract_button";
export declare class CheckboxButtonGroupView extends WidgetView {
    model: CheckboxButtonGroup;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
}
export declare namespace CheckboxButtonGroup {
    interface Attrs extends Widget.Attrs {
        active: number[];
        labels: string[];
        button_type: ButtonType;
        callback: any;
    }
    interface Props extends Widget.Props {
    }
}
export interface CheckboxButtonGroup extends CheckboxButtonGroup.Attrs {
}
export declare class CheckboxButtonGroup extends Widget {
    properties: CheckboxButtonGroup.Props;
    constructor(attrs?: Partial<CheckboxButtonGroup.Attrs>);
    change_input(i: number): void;
    static initClass(): void;
}
