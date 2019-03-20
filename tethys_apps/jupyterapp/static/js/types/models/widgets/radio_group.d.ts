import { Widget, WidgetView } from "./widget";
export declare class RadioGroupView extends WidgetView {
    model: RadioGroup;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    change_input(): void;
}
export declare namespace RadioGroup {
    interface Attrs extends Widget.Attrs {
        active: number;
        labels: string[];
        inline: boolean;
        callback: any;
    }
    interface Props extends Widget.Props {
    }
}
export interface RadioGroup extends RadioGroup.Attrs {
}
export declare class RadioGroup extends Widget {
    properties: RadioGroup.Props;
    constructor(attrs?: Partial<RadioGroup.Attrs>);
    static initClass(): void;
}
