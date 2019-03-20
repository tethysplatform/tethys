declare const enum Direction {
    clock = 0,
    anticlock = 1
}
export declare function angle_norm(angle: number): number;
export declare function angle_dist(lhs: number, rhs: number): number;
export declare function angle_between(mid: number, lhs: number, rhs: number, direction: Direction): boolean;
export declare function random(): number;
export declare function randomIn(min: number, max?: number): number;
export declare function atan2(start: [number, number], end: [number, number]): number;
export declare function rnorm(mu: number, sigma: number): number;
export declare function clamp(val: number, min: number, max: number): number;
export {};
