import { Widget, WidgetView } from "./widget";
import * as p from "core/properties";
export declare class InputWidgetView extends WidgetView {
    model: InputWidget;
    change_input(): void;
}
export declare namespace InputWidget {
    interface Attrs extends Widget.Attrs {
        title: string;
        callback: any | null;
    }
    interface Props extends Widget.Props {
        title: p.Property<string>;
    }
}
export interface InputWidget extends InputWidget.Attrs {
}
export declare class InputWidget extends Widget {
    properties: InputWidget.Props;
    constructor(attrs?: Partial<InputWidget.Attrs>);
    static initClass(): void;
}
