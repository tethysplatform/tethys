import { Widget, WidgetView } from "./widget";
export declare class CheckboxGroupView extends WidgetView {
    model: CheckboxGroup;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    change_input(): void;
}
export declare namespace CheckboxGroup {
    interface Attrs extends Widget.Attrs {
        active: number[];
        labels: string[];
        inline: boolean;
        callback: any;
    }
    interface Props extends Widget.Props {
    }
}
export interface CheckboxGroup extends CheckboxGroup.Attrs {
}
export declare class CheckboxGroup extends Widget {
    properties: CheckboxGroup.Props;
    constructor(attrs?: Partial<CheckboxGroup.Attrs>);
    static initClass(): void;
}
