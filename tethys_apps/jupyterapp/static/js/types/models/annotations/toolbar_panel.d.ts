import { Annotation, AnnotationView } from "./annotation";
import { Toolbar } from "../tools/toolbar";
import { ToolbarBaseView } from "../tools/toolbar_base";
export declare class ToolbarPanelView extends AnnotationView {
    model: ToolbarPanel;
    protected _toolbar_views: {
        [key: string]: ToolbarBaseView;
    };
    initialize(options: any): void;
    remove(): void;
    render(): void;
    protected _get_size(): number;
}
export declare namespace ToolbarPanel {
    interface Attrs extends Annotation.Attrs {
        toolbar: Toolbar;
    }
    interface Props extends Annotation.Props {
    }
}
export interface ToolbarPanel extends ToolbarPanel.Attrs {
}
export declare class ToolbarPanel extends Annotation {
    properties: ToolbarPanel.Props;
    constructor(attrs?: Partial<ToolbarPanel.Attrs>);
    static initClass(): void;
}
