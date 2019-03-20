import { Location, SizingMode } from "core/enums";
import { Tool } from "./tool";
import { ToolbarBase, ToolbarBaseView } from "./toolbar_base";
import { ToolProxy } from "./tool_proxy";
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
export declare namespace ProxyToolbar {
    interface Attrs extends ToolbarBase.Attrs {
    }
    interface Props extends ToolbarBase.Props {
    }
}
export interface ProxyToolbar extends ProxyToolbar.Attrs {
}
export declare class ProxyToolbar extends ToolbarBase {
    properties: ProxyToolbar.Props;
    constructor(attrs?: Partial<ProxyToolbar.Attrs>);
    static initClass(): void;
    _proxied_tools: (Tool | ToolProxy)[];
    initialize(): void;
    protected _init_tools(): void;
    protected _merge_tools(): void;
}
export declare class ToolbarBoxView extends LayoutDOMView {
    model: ToolbarBox;
    protected _toolbar_views: {
        [key: string]: ToolbarBaseView;
    };
    initialize(options: any): void;
    remove(): void;
    css_classes(): string[];
    render(): void;
    get_width(): number;
    get_height(): number;
}
export declare namespace ToolbarBox {
    interface Attrs extends LayoutDOM.Attrs {
        toolbar: ToolbarBase;
        toolbar_location: Location;
    }
    interface Props extends LayoutDOM.Props {
    }
}
export interface ToolbarBox extends ToolbarBox.Attrs {
}
export declare class ToolbarBox extends LayoutDOM {
    properties: ToolbarBox.Props;
    constructor(attrs?: Partial<ToolbarBox.Attrs>);
    static initClass(): void;
    readonly sizing_mode: SizingMode;
}
