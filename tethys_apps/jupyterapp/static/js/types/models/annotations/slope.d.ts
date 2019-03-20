import { Annotation, AnnotationView } from "./annotation";
import { LineMixinScalar } from "core/property_mixins";
import { Line } from "core/visuals";
import { Color } from "core/types";
import * as p from "core/properties";
export declare class SlopeView extends AnnotationView {
    model: Slope;
    visuals: Slope.Visuals;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    protected _draw_slope(): void;
}
export declare namespace Slope {
    interface Mixins extends LineMixinScalar {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        gradient: number | null;
        y_intercept: number | null;
        x_range_name: string;
        y_range_name: string;
    }
    interface Props extends Annotation.Props {
        gradient: p.Property<number | null>;
        y_intercept: p.Property<number | null>;
        x_range_name: p.Property<string>;
        y_range_name: p.Property<string>;
        line_color: p.Property<Color>;
        line_width: p.Property<number>;
        line_alpha: p.Property<number>;
    }
    type Visuals = Annotation.Visuals & {
        line: Line;
    };
}
export interface Slope extends Slope.Attrs {
}
export declare class Slope extends Annotation {
    properties: Slope.Props;
    constructor(attrs?: Partial<Slope.Attrs>);
    static initClass(): void;
}
