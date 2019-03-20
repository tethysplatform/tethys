import { Rect } from "./spatial";
export declare function empty(): Rect;
export declare function positive_x(): Rect;
export declare function positive_y(): Rect;
export declare function union(a: Rect, b: Rect): Rect;
export interface IBBox {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
}
export interface IRect {
    x: number;
    y: number;
    width: number;
    height: number;
}
export interface IRange {
    start: number;
    end: number;
}
export declare class BBox implements IBBox {
    readonly x0: number;
    readonly y0: number;
    readonly x1: number;
    readonly y1: number;
    constructor(box: IBBox | IRect);
    readonly minX: number;
    readonly minY: number;
    readonly maxX: number;
    readonly maxY: number;
    readonly left: number;
    readonly top: number;
    readonly right: number;
    readonly bottom: number;
    readonly p0: [number, number];
    readonly p1: [number, number];
    readonly x: number;
    readonly y: number;
    readonly width: number;
    readonly height: number;
    readonly rect: IRect;
    readonly h_range: IRange;
    readonly v_range: IRange;
    readonly ranges: [IRange, IRange];
    readonly aspect: number;
    contains(x: number, y: number): boolean;
    clip(x: number, y: number): [number, number];
    union(that: IBBox): BBox;
}
