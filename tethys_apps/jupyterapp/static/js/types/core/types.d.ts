export declare type Anything = any;
export declare type Color = string;
export declare type TypedArray = Uint8Array | Int8Array | Uint16Array | Int16Array | Uint32Array | Int32Array | Float32Array | Float64Array;
export interface Arrayable<T = Anything> {
    readonly length: number;
    [n: number]: T;
}
