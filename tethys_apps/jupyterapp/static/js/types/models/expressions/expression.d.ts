import { ColumnarDataSource } from "../sources/columnar_data_source";
import { Model } from "../../model";
import { Arrayable } from "core/types";
export declare namespace Expression {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface Expression extends Expression.Attrs {
}
export declare abstract class Expression extends Model {
    properties: Expression.Props;
    constructor(attrs?: Partial<Expression.Attrs>);
    static initClass(): void;
    protected _connected: {
        [key: string]: boolean;
    };
    protected _result: {
        [key: string]: Arrayable;
    };
    initialize(): void;
    protected abstract _v_compute(source: ColumnarDataSource): Arrayable;
    v_compute(source: ColumnarDataSource): Arrayable;
}
