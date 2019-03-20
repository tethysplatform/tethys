import { OutputBackend } from "../enums";
import SVGRenderingContext2D = require("canvas2svg");
export { SVGRenderingContext2D };
export declare type Context2d = {
    setLineDashOffset(offset: number): void;
    getLineDashOffset(): number;
    setImageSmoothingEnabled(value: boolean): void;
    getImageSmoothingEnabled(): boolean;
    measureText(text: string): TextMetrics & {
        ascent: number;
    };
} & CanvasRenderingContext2D;
export declare function fixup_ctx(ctx: any): void;
export declare function get_scale_ratio(ctx: any, hidpi: boolean, backend: OutputBackend): number;
