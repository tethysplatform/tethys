import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
export declare abstract class WidgetView extends LayoutDOMView {
    model: Widget;
    css_classes(): string[];
    render(): void;
    get_width(): number;
    get_height(): number;
}
export declare namespace Widget {
    interface Attrs extends LayoutDOM.Attrs {
    }
    interface Props extends LayoutDOM.Props {
    }
}
export interface Widget extends Widget.Attrs {
}
export declare abstract class Widget extends LayoutDOM {
    properties: Widget.Props;
    constructor(attrs?: Partial<Widget.Attrs>);
    static initClass(): void;
}
