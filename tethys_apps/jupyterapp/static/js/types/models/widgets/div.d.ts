import { Markup, MarkupView } from "./markup";
export declare class DivView extends MarkupView {
    model: Div;
    render(): void;
}
export declare namespace Div {
    interface Attrs extends Markup.Attrs {
        render_as_text: boolean;
    }
    interface Props extends Markup.Props {
    }
}
export interface Div extends Div.Attrs {
}
export declare class Div extends Markup {
    properties: Div.Props;
    constructor(attrs?: Partial<Div.Attrs>);
    static initClass(): void;
}
