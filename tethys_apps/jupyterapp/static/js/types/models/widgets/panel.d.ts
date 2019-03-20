import { Widget, WidgetView } from "./widget";
import { LayoutDOM } from "../layouts/layout_dom";
export declare class PanelView extends WidgetView {
    model: Panel;
    render(): void;
}
export declare namespace Panel {
    interface Attrs extends Widget.Attrs {
        title: string;
        child: LayoutDOM;
        closable: boolean;
    }
    interface Props extends Widget.Props {
    }
}
export interface Panel extends Panel.Attrs {
}
export declare class Panel extends Widget {
    properties: Panel.Props;
    constructor(attrs?: Partial<Panel.Attrs>);
    static initClass(): void;
}
