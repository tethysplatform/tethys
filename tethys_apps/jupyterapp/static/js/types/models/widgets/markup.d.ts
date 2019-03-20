import { Widget, WidgetView } from "./widget";
export declare class MarkupView extends WidgetView {
    model: Markup;
    protected markupEl: HTMLElement;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
}
export declare namespace Markup {
    interface Attrs extends Widget.Attrs {
        text: string;
        style: {
            [key: string]: string;
        };
    }
    interface Props extends Widget.Props {
    }
}
export interface Markup extends Markup.Attrs {
}
export declare class Markup extends Widget {
    properties: Markup.Props;
    constructor(attrs?: Partial<Markup.Attrs>);
    static initClass(): void;
}
