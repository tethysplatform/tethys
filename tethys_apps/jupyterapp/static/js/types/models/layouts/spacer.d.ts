import { LayoutDOM, LayoutDOMView } from "./layout_dom";
import { Variable } from "core/layout/solver";
export declare class SpacerView extends LayoutDOMView {
    model: Spacer;
    render(): void;
    css_classes(): string[];
    get_width(): number;
    get_height(): number;
}
export declare namespace Spacer {
    interface Attrs extends LayoutDOM.Attrs {
    }
    interface Props extends LayoutDOM.Props {
    }
}
export interface Spacer extends Spacer.Attrs {
}
export declare class Spacer extends LayoutDOM {
    properties: Spacer.Props;
    constructor(attrs?: Partial<Spacer.Attrs>);
    static initClass(): void;
    get_constrained_variables(): {
        [key: string]: Variable;
    };
}
