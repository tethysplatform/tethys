import * as p from "core/properties";
import { Widget, WidgetView } from "./widget";
import { Panel } from "./panel";
import { LayoutDOM } from "../layouts/layout_dom";
export declare class TabsView extends WidgetView {
    model: Tabs;
    connect_signals(): void;
    render(): void;
}
export declare namespace Tabs {
    interface Attrs extends Widget.Attrs {
        tabs: Panel[];
        active: number;
        callback: any;
    }
    interface Props extends Widget.Props {
        tabs: p.Property<Panel[]>;
        active: p.Property<number>;
    }
}
export interface Tabs extends Tabs.Attrs {
}
export declare class Tabs extends Widget {
    properties: Tabs.Props;
    constructor(attrs?: Partial<Tabs.Attrs>);
    static initClass(): void;
    get_layoutable_children(): LayoutDOM[];
    readonly children: LayoutDOM[];
}
