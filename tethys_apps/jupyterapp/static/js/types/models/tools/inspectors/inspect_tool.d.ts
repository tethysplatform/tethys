import { ButtonTool, ButtonToolView } from "../button_tool";
export declare abstract class InspectToolView extends ButtonToolView {
    model: InspectTool;
}
export declare namespace InspectTool {
    interface Attrs extends ButtonTool.Attrs {
        toggleable: boolean;
    }
    interface Props extends ButtonTool.Props {
    }
}
export interface InspectTool extends InspectTool.Attrs {
}
export declare abstract class InspectTool extends ButtonTool {
    properties: InspectTool.Props;
    constructor(attrs?: Partial<InspectTool.Attrs>);
    static initClass(): void;
    event_type: "move";
}
