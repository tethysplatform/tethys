import { Palette } from "./palettes";
import { Plot } from "./models";
export declare type Color = string;
export interface ChartOpts {
    width?: number;
    height?: number;
}
export interface PieChartData {
    labels: number[];
    values: number[];
}
export interface PieChartOpts extends ChartOpts {
    start_angle?: number;
    end_angle?: number;
    center?: [number, number] | {
        x: number;
        y: number;
    };
    inner_radius?: number;
    outer_radius?: number;
    palette?: Palette | Color[];
    slice_labels?: "labels" | "values" | "percentages";
}
export declare function pie(data: PieChartData, opts?: PieChartOpts): Plot;
export declare type BarChartData = number[][];
export interface BarChartOpts extends ChartOpts {
    stacked?: boolean;
    orientation?: "horizontal" | "vertical";
    bar_width?: number;
    palette?: Palette | Color[];
    axis_number_format?: string;
}
export declare function bar(data: BarChartData, opts?: BarChartOpts): Plot;
