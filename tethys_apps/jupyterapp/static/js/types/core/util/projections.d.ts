import { LatLon } from "../enums";
export declare const wgs84_mercator: {
    forward: (coords: [number, number]) => [number, number];
    inverse: (coords: [number, number]) => [number, number];
};
export declare function clip_mercator(low: number, high: number, dimension: LatLon): [number, number];
export declare function in_bounds(value: number, dimension: LatLon): boolean;
export declare function project_xy(x: number[], y: number[]): [number[], number[]];
export declare function project_xsys(xs: number[][], ys: number[][]): [number[][], number[][]];
