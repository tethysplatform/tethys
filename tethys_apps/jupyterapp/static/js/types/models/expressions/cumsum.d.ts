import { ColumnarDataSource } from "../sources/columnar_data_source";
import { Expression } from "./expression";
import { Arrayable } from "core/types";
export declare namespace CumSum {
    interface Attrs extends Expression.Attrs {
        field: string;
        include_zero: boolean;
    }
    interface Props extends Expression.Props {
    }
}
export interface CumSum extends CumSum.Attrs {
}
export declare class CumSum extends Expression {
    properties: CumSum.Props;
    constructor(attrs?: Partial<CumSum.Attrs>);
    static initClass(): void;
    protected _v_compute(source: ColumnarDataSource): Arrayable<number>;
}
