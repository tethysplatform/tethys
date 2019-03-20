import { ColumnarDataSource } from "../sources/columnar_data_source";
import { Expression } from "./expression";
import { Arrayable } from "core/types";
export declare namespace Stack {
    interface Attrs extends Expression.Attrs {
        fields: string[];
    }
    interface Props extends Expression.Props {
    }
}
export interface Stack extends Stack.Attrs {
}
export declare class Stack extends Expression {
    properties: Stack.Props;
    constructor(attrs?: Partial<Stack.Attrs>);
    static initClass(): void;
    protected _v_compute(source: ColumnarDataSource): Arrayable<number>;
}
