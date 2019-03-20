import { ButtonTool, ButtonToolView } from "../button_tool";
import { OnOffButtonView } from "../on_off_button";
export declare abstract class GestureToolView extends ButtonToolView {
    model: GestureTool;
}
export declare namespace GestureTool {
    interface Attrs extends ButtonTool.Attrs {
    }
    interface Props extends ButtonTool.Props {
    }
}
export interface GestureTool extends GestureTool.Attrs {
}
export declare abstract class GestureTool extends ButtonTool {
    properties: GestureTool.Props;
    constructor(attrs?: Partial<GestureTool.Attrs>);
    static initClass(): void;
    button_view: typeof OnOffButtonView;
    default_order: number;
}
