import { Annotation, AnnotationView } from "./annotation";
import { LineMixinScalar, FillMixinScalar } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { SpatialUnits } from "core/enums";
import { Signal0 } from "core/signaling";
export declare class PolyAnnotationView extends AnnotationView {
    model: PolyAnnotation;
    visuals: PolyAnnotation.Visuals;
    connect_signals(): void;
    render(): void;
}
export declare namespace PolyAnnotation {
    interface Mixins extends LineMixinScalar, FillMixinScalar {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        xs: number[];
        xs_units: SpatialUnits;
        ys: number[];
        ys_units: SpatialUnits;
        x_range_name: string;
        y_range_name: string;
        screen: boolean;
    }
    interface Props extends Annotation.Props {
    }
    type Visuals = Annotation.Visuals & {
        line: Line;
        fill: Fill;
    };
}
export interface PolyAnnotation extends PolyAnnotation.Attrs {
}
export declare class PolyAnnotation extends Annotation {
    properties: PolyAnnotation.Props;
    data_update: Signal0<this>;
    constructor(attrs?: Partial<PolyAnnotation.Attrs>);
    static initClass(): void;
    initialize(): void;
    update({ xs, ys }: {
        xs: number[];
        ys: number[];
    }): void;
}
