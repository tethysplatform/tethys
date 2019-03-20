import { GuideRenderer, GuideRendererView } from "../renderers/guide_renderer";
import { Range } from "../ranges/range";
import { Ticker } from "../tickers/ticker";
import { Line, Fill } from "core/visuals";
import { Color } from "core/types";
import { LineJoin, LineCap } from "core/enums";
import { Context2d } from "core/util/canvas";
export declare class GridView extends GuideRendererView {
    model: Grid;
    visuals: Grid.Visuals;
    protected readonly _x_range_name: string;
    protected readonly _y_range_name: string;
    render(): void;
    connect_signals(): void;
    protected _draw_regions(ctx: Context2d): void;
    protected _draw_grids(ctx: Context2d): void;
    protected _draw_minor_grids(ctx: Context2d): void;
    protected _draw_grid_helper(ctx: Context2d, visuals: Line, xs: number[][], ys: number[][]): void;
}
export declare namespace Grid {
    interface GridLine {
        grid_line_color: Color;
        grid_line_width: number;
        grid_line_alpha: number;
        grid_line_join: LineJoin;
        grid_line_cap: LineCap;
        grid_line_dash: number[];
        grid_line_dash_offset: number;
    }
    interface MinorGridLine {
        minor_grid_line_color: Color;
        minor_grid_line_width: number;
        minor_grid_line_alpha: number;
        minor_grid_line_join: LineJoin;
        minor_grid_line_cap: LineCap;
        minor_grid_line_dash: number[];
        minor_grid_line_dash_offset: number;
    }
    interface BandFill {
        fill_color: Color;
        fill_alpha: number;
    }
    interface Mixins extends GridLine, MinorGridLine, BandFill {
    }
    interface Attrs extends GuideRenderer.Attrs, Mixins {
        bounds: [number, number] | "auto";
        dimension: 0 | 1;
        ticker: Ticker<any>;
        x_range_name: string;
        y_range_name: string;
    }
    interface Props extends GuideRenderer.Props {
    }
    type Visuals = GuideRenderer.Visuals & {
        grid_line: Line;
        minor_grid_line: Line;
        band_fill: Fill;
    };
}
export interface Grid extends Grid.Attrs {
}
export declare class Grid extends GuideRenderer {
    properties: Grid.Props;
    constructor(attrs?: Partial<Grid.Attrs>);
    static initClass(): void;
    ranges(): [Range, Range];
    computed_bounds(): [number, number];
    grid_coords(location: "major" | "minor", exclude_ends?: boolean): [number[][], number[][]];
}
