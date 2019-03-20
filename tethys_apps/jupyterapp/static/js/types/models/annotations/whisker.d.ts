import { Annotation, AnnotationView } from "./annotation";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { ArrowHead } from "./arrow_head";
import { DistanceSpec } from "core/vectorization";
import { LineMixinVector } from "core/property_mixins";
import { Line } from "core/visuals";
import { Arrayable } from "core/types";
import { Dimension } from "core/enums";
export declare class WhiskerView extends AnnotationView {
    model: Whisker;
    visuals: Whisker.Visuals;
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
export declare namespace Whisker {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends Annotation.Attrs, Mixins {
        lower: DistanceSpec;
        lower_head: ArrowHead;
        upper: DistanceSpec;
        upper_head: ArrowHead;
        base: DistanceSpec;
        dimension: Dimension;
        source: ColumnarDataSource;
        x_range_name: string;
        y_range_name: string;
    }
    interface Props extends Annotation.Props {
    }
    type Visuals = Annotation.Visuals & {
        line: Line;
    };
}
export interface Whisker extends Whisker.Attrs {
}
export declare class Whisker extends Annotation {
    properties: Whisker.Props;
    constructor(attrs?: Partial<Whisker.Attrs>);
    static initClass(): void;
}
