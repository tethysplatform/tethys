import { DOMView } from "core/dom_view";
import * as visuals from "core/visuals";
import { RenderLevel } from "core/enums";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import { Model } from "../../model";
import { BBox } from "core/util/bbox";
import { PlotCanvas, PlotCanvasView } from "../plots/plot_canvas";
export declare abstract class RendererView extends DOMView {
    model: Renderer;
    visuals: Renderer.Visuals;
    plot_view: PlotCanvasView;
    initialize(options: any): void;
    readonly plot_model: PlotCanvas;
    request_render(): void;
    map_to_screen(x: Arrayable<number>, y: Arrayable<number>): [Arrayable<number>, Arrayable<number>];
    interactive_bbox?(sx: number, sy: number): BBox;
    interactive_hit?(sx: number, sy: number): boolean;
    readonly needs_clip: boolean;
}
export declare namespace Renderer {
    interface Attrs extends Model.Attrs {
        level: RenderLevel;
        visible: boolean;
    }
    interface Props extends Model.Props {
        level: p.Property<RenderLevel>;
        visible: p.Property<boolean>;
    }
    type Visuals = visuals.Visuals;
}
export interface Renderer extends Renderer.Attrs {
}
export declare abstract class Renderer extends Model {
    properties: Renderer.Props;
    constructor(attrs?: Partial<Renderer.Attrs>);
    static initClass(): void;
}
