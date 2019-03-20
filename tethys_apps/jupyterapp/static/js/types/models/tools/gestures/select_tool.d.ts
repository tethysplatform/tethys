import { GestureTool, GestureToolView } from "./gesture_tool";
import { DataRenderer, RendererSpec } from "../util";
import { KeyEvent } from "core/ui_events";
import { Geometry } from "core/geometry";
export declare abstract class SelectToolView extends GestureToolView {
    model: SelectTool;
    readonly computed_renderers: DataRenderer[];
    _computed_renderers_by_data_source(): {
        [key: string]: DataRenderer[];
    };
    _keyup(ev: KeyEvent): void;
    _select(geometry: Geometry, final: boolean, append: boolean): void;
    _emit_selection_event(geometry: Geometry, final?: boolean): void;
}
export declare namespace SelectTool {
    interface Attrs extends GestureTool.Attrs {
        renderers: RendererSpec;
        names: string[];
    }
    interface Props extends GestureTool.Props {
    }
}
export interface SelectTool extends SelectTool.Attrs {
}
export declare abstract class SelectTool extends GestureTool {
    properties: SelectTool.Props;
    constructor(attrs?: Partial<SelectTool.Attrs>);
    static initClass(): void;
}
