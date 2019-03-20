import { Marker } from "./marker";
import { Class } from "core/class";
import { Line, Fill } from "core/visuals";
import { Context2d } from "core/util/canvas";
export declare type RenderOne = (ctx: Context2d, i: number, r: number, line: Line, fill: Fill) => void;
export declare const Asterisk: Class<Marker>;
export declare const CircleCross: Class<Marker>;
export declare const CircleX: Class<Marker>;
export declare const Cross: Class<Marker>;
export declare const Diamond: Class<Marker>;
export declare const DiamondCross: Class<Marker>;
export declare const Hex: Class<Marker>;
export declare const InvertedTriangle: Class<Marker>;
export declare const Square: Class<Marker>;
export declare const SquareCross: Class<Marker>;
export declare const SquareX: Class<Marker>;
export declare const Triangle: Class<Marker>;
export declare const Dash: Class<Marker>;
export declare const X: Class<Marker>;
interface FuncsMap {
    [s: string]: RenderOne;
}
export declare const marker_funcs: FuncsMap;
export {};
