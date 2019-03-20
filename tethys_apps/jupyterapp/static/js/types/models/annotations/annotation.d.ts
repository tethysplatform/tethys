import { SidePanel } from "core/layout/side_panel";
import { Side } from "core/enums";
import * as p from "core/properties";
import { Renderer, RendererView } from "../renderers/renderer";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { Plot } from "../plots/plot";
export declare abstract class AnnotationView extends RendererView {
    model: Annotation;
    protected _get_size(): number;
    get_size(): number;
    set_data(source: ColumnarDataSource): void;
}
export declare namespace Annotation {
    interface Attrs extends Renderer.Attrs {
        plot: Plot;
    }
    interface Props extends Renderer.Props {
        plot: p.Property<Plot>;
    }
    type Visuals = Renderer.Visuals;
}
export interface Annotation extends Annotation.Attrs {
    panel?: SidePanel;
}
export declare abstract class Annotation extends Renderer {
    properties: Annotation.Props;
    constructor(attrs?: Partial<Annotation.Attrs>);
    static initClass(): void;
    add_panel(side: Side): void;
    set_panel(panel: SidePanel): void;
}
