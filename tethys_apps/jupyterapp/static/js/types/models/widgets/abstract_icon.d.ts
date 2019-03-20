import { Widget, WidgetView } from "./widget";
export declare abstract class AbstractIconView extends WidgetView {
    model: AbstractIcon;
}
export declare namespace AbstractIcon {
    interface Attrs extends Widget.Attrs {
    }
    interface Props extends Widget.Props {
    }
}
export interface AbstractIcon extends AbstractIcon.Attrs {
}
export declare abstract class AbstractIcon extends Widget {
    properties: AbstractIcon.Props;
    constructor(attrs?: Partial<AbstractIcon.Attrs>);
    static initClass(): void;
}
