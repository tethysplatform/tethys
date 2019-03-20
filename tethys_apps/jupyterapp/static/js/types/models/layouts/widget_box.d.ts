import * as p from "core/properties";
import { Variable } from "core/layout/solver";
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
export declare class WidgetBoxView extends LayoutDOMView {
    model: WidgetBox;
    connect_signals(): void;
    css_classes(): string[];
    render(): void;
    get_height(): number;
    get_width(): number;
}
export declare namespace WidgetBox {
    interface Attrs extends LayoutDOM.Attrs {
        children: LayoutDOM[];
    }
    interface Props extends LayoutDOM.Props {
        children: p.Property<LayoutDOM[]>;
    }
}
export interface WidgetBox extends WidgetBox.Attrs {
}
export declare class WidgetBox extends LayoutDOM {
    properties: WidgetBox.Props;
    constructor(attrs?: Partial<WidgetBox.Attrs>);
    static initClass(): void;
    initialize(): void;
    get_constrained_variables(): {
        [key: string]: Variable;
    };
    get_layoutable_children(): LayoutDOM[];
}
