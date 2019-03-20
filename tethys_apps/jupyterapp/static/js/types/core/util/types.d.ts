import { Anything, Arrayable, TypedArray } from "../types";
export declare function isBoolean(obj: Anything): obj is boolean;
export declare function isNumber(obj: Anything): obj is number;
export declare function isInteger(obj: Anything): obj is number;
export declare function isString(obj: Anything): obj is string;
export declare function isStrictNaN(obj: Anything): obj is number;
export declare function isFunction(obj: Anything): obj is Function;
export declare function isArray<T>(obj: Anything): obj is T[];
export declare function isArrayOf<T>(arr: Anything[], predicate: (item: Anything) => item is T): arr is T[];
export declare function isArrayableOf<T>(arr: Arrayable, predicate: (item: Anything) => item is T): arr is Arrayable<T>;
export declare function isTypedArray(obj: Anything): obj is TypedArray;
export declare function isObject(obj: Anything): obj is object;
export declare function isPlainObject(obj: Anything): obj is {
    [key: string]: unknown;
};
