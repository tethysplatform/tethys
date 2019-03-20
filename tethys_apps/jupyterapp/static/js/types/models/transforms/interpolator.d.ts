import { Transform } from "./transform";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import { Arrayable } from "core/types";
export declare namespace Interpolator {
    interface Attrs extends Transform.Attrs {
        x: string | number[];
        y: string | number[];
        data: ColumnarDataSource | null;
        clip: boolean;
    }
    interface Props extends Transform.Props {
    }
}
export interface Interpolator extends Interpolator.Attrs {
}
export declare abstract class Interpolator extends Transform {
    properties: Interpolator.Props;
    constructor(attrs?: Partial<Interpolator.Attrs>);
    static initClass(): void;
    protected _x_sorted: number[];
    protected _y_sorted: number[];
    protected _sorted_dirty: boolean;
    connect_signals(): void;
    v_compute(xs: Arrayable<number>): Arrayable<number>;
    sort(descending?: boolean): void;
}
