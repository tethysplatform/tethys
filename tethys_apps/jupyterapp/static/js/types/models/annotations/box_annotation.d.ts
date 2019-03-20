import { Annotation, AnnotationView } from "./annotation";
import { Signal0 } from "core/signaling";
import { LineMixinScalar, FillMixinScalar } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { SpatialUnits, RenderMode } from "core/enums";
import { Color } from "core/types";
import * as p from "core/properties";
import { BBox } from "core/util/bbox";
export declare const EDGE_TOLERANCE = 2.5;
export declare class BoxAnnotationView extends AnnotationView {
    model: BoxAnnotation;
    visuals: BoxAnnotation.Visuals;
    private sleft;
    private sright;
    private sbottom;
    private stop;
    initialize(options: any): void;
    connect_signals(): void;
    render(): void;
    protected _css_box(sleft: number, sright: number, sbottom: number, stop: number): void;
    protected _canvas_box(sleft: number, sright: number, sbottom: number, stop: number): void;
    interactive_bbox(): BBox;
    interactive_hit(sx: number, sy: number): boolean;
    cursor(sx: number, sy: number): string | null;
}
export declare namespace BoxAnnotation {
    interface Mixins extends LineMixinScalar, FillMixinScalar {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        render_mode: RenderMode;
        x_range_name: string;
        y_range_name: string;
        top: number | null;
        top_units: SpatialUnits;
        bottom: number | null;
        bottom_units: SpatialUnits;
        left: number | null;
        left_units: SpatialUnits;
        right: number | null;
        right_units: SpatialUnits;
        screen: boolean;
        ew_cursor: string | null;
        ns_cursor: string | null;
        in_cursor: string | null;
    }
    interface Props extends Annotation.Props {
        render_mode: p.Property<RenderMode>;
        x_range_name: p.Property<string>;
        y_range_name: p.Property<string>;
        top: p.Property<number | null>;
        top_units: p.Property<SpatialUnits>;
        bottom: p.Property<number | null>;
        bottom_units: p.Property<SpatialUnits>;
        left: p.Property<number | null>;
        left_units: p.Property<SpatialUnits>;
        right: p.Property<number | null>;
        right_units: p.Property<SpatialUnits>;
        line_color: p.Property<Color>;
        line_width: p.Property<number>;
        line_dash: p.Property<number[]>;
        fill_color: p.Property<Color>;
        fill_alpha: p.Property<number>;
    }
    type Visuals = Annotation.Visuals & {
        line: Line;
        fill: Fill;
    };
}
export interface BoxAnnotation extends BoxAnnotation.Attrs {
}
export declare class BoxAnnotation extends Annotation {
    properties: BoxAnnotation.Props;
    constructor(attrs?: Partial<BoxAnnotation.Attrs>);
    static initClass(): void;
    data_update: Signal0<this>;
    initialize(): void;
    update({ left, right, top, bottom }: {
        left: number | null;
        right: number | null;
        top: number | null;
        bottom: number | null;
    }): void;
}
