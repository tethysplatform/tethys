import { Color } from "./types";
import { SpatialUnits, AngleUnits } from "./enums";
export interface Value<T> {
    value: T;
}
export interface Field {
    field: string;
}
export declare type Scalar<T> = T | null | Value<T>;
export declare type Vectorized<T> = T | null | Value<T> | Field;
export declare type AngleSpec = Vectorized<number> & {
    units?: AngleUnits;
};
export declare type ColorSpec = Vectorized<Color>;
export declare type DistanceSpec = Vectorized<number> & {
    units?: SpatialUnits;
};
export declare type FontSizeSpec = Vectorized<string>;
export declare type NumberSpec = Vectorized<number>;
export declare type StringSpec = Vectorized<string>;
export declare function isValue<T>(obj: Scalar<T> | Vectorized<T>): obj is Value<T>;
export declare function isField<T>(obj: Vectorized<T>): obj is Field;
