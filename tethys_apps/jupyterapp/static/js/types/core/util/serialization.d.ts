import { Arrayable, TypedArray } from "../types";
export declare const ARRAY_TYPES: {
    uint8: Uint8ArrayConstructor;
    int8: Int8ArrayConstructor;
    uint16: Uint16ArrayConstructor;
    int16: Int16ArrayConstructor;
    uint32: Uint32ArrayConstructor;
    int32: Int32ArrayConstructor;
    float32: Float32ArrayConstructor;
    float64: Float64ArrayConstructor;
};
export declare const DTYPES: {
    Uint8Array: "uint8";
    Int8Array: "int8";
    Uint16Array: "uint16";
    Int16Array: "int16";
    Uint32Array: "uint32";
    Int32Array: "int32";
    Float32Array: "float32";
    Float64Array: "float64";
};
export declare type ArrayName = keyof typeof DTYPES;
export declare type DType = keyof typeof ARRAY_TYPES;
export declare type ByteOrder = "little" | "big";
export declare const BYTE_ORDER: ByteOrder;
export declare function swap16(a: Int16Array | Uint16Array): void;
export declare function swap32(a: Int32Array | Uint32Array | Float32Array): void;
export declare function swap64(a: Float64Array): void;
export declare type Shape = number[];
export interface BufferSpec {
    __buffer__: string;
    order: ByteOrder;
    dtype: DType;
    shape: Shape;
}
export declare function process_buffer(spec: BufferSpec, buffers: [any, any][]): [TypedArray, Shape];
export declare function process_array(obj: NDArray | BufferSpec | Arrayable, buffers: [any, any][]): [Arrayable, number[]];
export declare function arrayBufferToBase64(buffer: ArrayBuffer): string;
export declare function base64ToArrayBuffer(base64: string): ArrayBuffer;
export interface NDArray {
    __ndarray__: string;
    shape?: Shape;
    dtype: DType;
}
export declare function decode_base64(input: NDArray): [TypedArray, Shape];
export declare function encode_base64(array: TypedArray, shape?: Shape): NDArray;
export declare type Data = {
    [key: string]: Arrayable;
};
export declare type Shapes = {
    [key: string]: Shape | Shape[];
};
export declare type EncodedData = {
    [key: string]: NDArray | Arrayable;
};
export declare function decode_column_data(data: EncodedData, buffers?: [any, any][]): [Data, Shapes];
export declare function encode_column_data(data: Data, shapes?: Shapes): EncodedData;
