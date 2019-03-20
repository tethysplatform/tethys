import { Renderer, RendererView } from "./renderer";
import { GlyphRenderer, GlyphRendererView } from "./glyph_renderer";
import { LayoutProvider } from "../graphs/layout_provider";
import { GraphHitTestPolicy } from "../graphs/graph_hit_test_policy";
import { Scale } from "../scales/scale";
import { SelectionManager } from "core/selection_manager";
export declare class GraphRendererView extends RendererView {
    model: GraphRenderer;
    node_view: GlyphRendererView;
    edge_view: GlyphRendererView;
    xscale: Scale;
    yscale: Scale;
    protected _renderer_views: {
        [key: string]: GlyphRendererView;
    };
    initialize(options: any): void;
    connect_signals(): void;
    set_data(request_render?: boolean): void;
    render(): void;
}
export declare namespace GraphRenderer {
    interface Attrs extends Renderer.Attrs {
        x_range_name: string;
        y_range_name: string;
        layout_provider: LayoutProvider;
        node_renderer: GlyphRenderer;
        edge_renderer: GlyphRenderer;
        selection_policy: GraphHitTestPolicy;
        inspection_policy: GraphHitTestPolicy;
    }
    interface Props extends Renderer.Props {
    }
}
export interface GraphRenderer extends GraphRenderer.Attrs {
}
export declare class GraphRenderer extends Renderer {
    properties: GraphRenderer.Props;
    constructor(attrs?: Partial<GraphRenderer.Attrs>);
    static initClass(): void;
    get_selection_manager(): SelectionManager;
}
