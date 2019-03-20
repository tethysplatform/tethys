import { Markup, MarkupView } from "./markup";
export declare class ParagraphView extends MarkupView {
    model: Paragraph;
    render(): void;
}
export declare namespace Paragraph {
    interface Attrs extends Markup.Attrs {
    }
    interface Props extends Markup.Props {
    }
}
export interface Paragraph extends Paragraph.Attrs {
}
export declare class Paragraph extends Markup {
    properties: Paragraph.Props;
    constructor(attrs?: Partial<Paragraph.Attrs>);
    static initClass(): void;
}
