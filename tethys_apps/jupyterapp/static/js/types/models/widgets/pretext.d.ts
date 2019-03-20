import { Markup, MarkupView } from "./markup";
export declare class PreTextView extends MarkupView {
    model: PreText;
    render(): void;
}
export declare namespace PreText {
    interface Attrs extends Markup.Attrs {
    }
    interface Props extends Markup.Props {
    }
}
export interface PreText extends PreText.Attrs {
}
export declare class PreText extends Markup {
    properties: PreText.Props;
    constructor(attrs?: Partial<PreText.Attrs>);
    static initClass(): void;
}
