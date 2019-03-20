import { Annotation, AnnotationView } from "./annotation";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { DistanceSpec } from "core/vectorization";
import { LineMixinScalar, FillMixinScalar } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { Arrayable } from "core/types";
import { Dimension } from "core/enums";
import * as p from "core/properties";
export declare class BandView extends AnnotationView {
    model: Band;
    visuals: Band.Visuals;
    protected _lower: Arrayable<number>;
    protected _upper: Arrayable<number>;
    protected _base: Arrayable<number>;
    protected max_lower: number;
    protected max_upper: number;
    protected max_base: number;
    protected _lower_sx: Arrayable<number>;
    protected _lower_sy: Arrayable<number>;
    protected _upper_sx: Arrayable<number>;
    protected _upper_sy: Arrayable<number>;
    initialize(options: any): void;
    connect_signals(): void;
    set_data(source: ColumnarDataSource): void;
    protected _map_data(): void;
    render(): void;
}
export declare namespace Band {
    interface Mixins extends LineMixinScalar, FillMixinScalar {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        lower: DistanceSpec;
        upper: DistanceSpec;
        base: DistanceSpec;
        dimension: Dimension;
        source: ColumnarDataSource;
        x_range_name: string;
        y_range_name: string;
    }
    interface Props extends Annotation.Props {
        lower: p.DistanceSpec;
        upper: p.DistanceSpec;
        base: p.DistanceSpec;
        dimension: p.Property<Dimension>;
        source: p.Property<ColumnarDataSource>;
        x_range_name: p.Property<string>;
        y_range_name: p.Property<string>;
    }
    type Visuals = Annotation.Visuals & {
        line: Line;
        fill: Fill;
    };
}
export interface Band extends Band.Attrs {
}
export declare class Band extends Annotation {
    properties: Band.Props;
    constructor(attrs?: Partial<Band.Attrs>);
    static initClass(): void;
}
