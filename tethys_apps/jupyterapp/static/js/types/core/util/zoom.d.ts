import { IRange } from "./bbox";
import { CartesianFrame } from "models/canvas/cartesian_frame";
import { Scale } from "models/scales/scale";
export declare function scale_highlow(range: IRange, factor: number, center?: number): [number, number];
export declare function get_info(scales: {
    [key: string]: Scale;
}, [sxy0, sxy1]: [number, number]): {
    [key: string]: IRange;
};
export declare function scale_range(frame: CartesianFrame, factor: number, h_axis?: boolean, v_axis?: boolean, center?: {
    x: number;
    y: number;
}): {
    xrs: {
        [key: string]: IRange;
    };
    yrs: {
        [key: string]: IRange;
    };
    factor: number;
};
