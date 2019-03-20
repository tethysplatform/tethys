import { Annotation, AnnotationView } from "./annotation";
import { LineMixinScalar } from "core/property_mixins";
import { Line } from "core/visuals";
import { SpatialUnits, RenderMode, Dimension } from "core/enums";
import { Color } from "core/types";
import * as p from "core/properties";
export declare class SpanView extends AnnotationView {
    model: Span;
    visuals: Span.Visuals;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    protected _draw_span(): void;
}
export declare namespace Span {
    interface Mixins extends LineMixinScalar {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        render_mode: RenderMode;
        x_range_name: string;
        y_range_name: string;
        location: number | null;
        location_units: SpatialUnits;
        dimension: Dimension;
        for_hover: boolean;
        computed_location: number | null;
    }
    interface Props extends Annotation.Props {
        render_mode: p.Property<RenderMode>;
        x_range_name: p.Property<string>;
        y_range_name: p.Property<string>;
        location: p.Property<number | null>;
        location_units: p.Property<SpatialUnits>;
        dimension: p.Property<Dimension>;
        for_hover: p.Property<boolean>;
        computed_location: p.Property<number | null>;
        line_color: p.Property<Color>;
        line_width: p.Property<number>;
        line_alpha: p.Property<number>;
    }
    type Visuals = Annotation.Visuals & {
        line: Line;
    };
}
export interface Span extends Span.Attrs {
}
export declare class Span extends Annotation {
    properties: Span.Props;
    constructor(attrs?: Partial<Span.Attrs>);
    static initClass(): void;
}
