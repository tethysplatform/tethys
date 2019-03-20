import { Renderer, RendererView } from "./renderer";
import { Plot } from "../plots/plot";
export declare abstract class GuideRendererView extends RendererView {
    model: GuideRenderer;
    visuals: GuideRenderer.Visuals;
}
export declare namespace GuideRenderer {
    interface Attrs extends Renderer.Attrs {
        plot: Plot;
    }
    interface Props extends Renderer.Props {
    }
    type Visuals = Renderer.Visuals;
}
export interface GuideRenderer extends GuideRenderer.Attrs {
}
export declare abstract class GuideRenderer extends Renderer {
    properties: GuideRenderer.Props;
    constructor(attrs?: Partial<GuideRenderer.Attrs>);
    static initClass(): void;
}
