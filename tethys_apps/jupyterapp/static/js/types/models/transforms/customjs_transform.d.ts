import { Transform } from "./transform";
import { Arrayable } from "core/types";
export declare namespace CustomJSTransform {
    interface Attrs extends Transform.Attrs {
        args: {
            [key: string]: any;
        };
        func: string;
        v_func: string;
        use_strict: boolean;
    }
    interface Props extends Transform.Props {
    }
}
export interface CustomJSTransform extends CustomJSTransform.Attrs {
}
export declare class CustomJSTransform extends Transform {
    properties: CustomJSTransform.Props;
    constructor(attrs?: Partial<CustomJSTransform.Attrs>);
    static initClass(): void;
    readonly names: string[];
    readonly values: any[];
    protected _make_transform(name: string, func: string): Function;
    readonly scalar_transform: Function;
    readonly vector_transform: Function;
    compute(x: number): number;
    v_compute(xs: Arrayable<number>): Arrayable<number>;
}
