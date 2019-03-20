import { Axis, AxisView, Extents, TickCoords, Coords } from "./axis";
import { CategoricalTicker } from "../tickers/categorical_ticker";
import { CategoricalTickFormatter } from "../formatters/categorical_tick_formatter";
import { Text, Line } from "core/visuals";
import { Color } from "core/types";
import { FontStyle, TextAlign, TextBaseline, LineJoin, LineCap, TickLabelOrientation } from "core/enums";
import { Context2d } from "core/util/canvas";
import { Orient } from "core/layout/side_panel";
export declare type CategoricalTickCoords = TickCoords & {
    mids: Coords;
    tops: Coords;
};
export declare class CategoricalAxisView extends AxisView {
    model: CategoricalAxis;
    visuals: CategoricalAxis.Visuals;
    protected _render(ctx: Context2d, extents: Extents, tick_coords: TickCoords): void;
    protected _draw_group_separators(ctx: Context2d, _extents: Extents, _tick_coords: TickCoords): void;
    protected _draw_major_labels(ctx: Context2d, extents: Extents, _tick_coords: TickCoords): void;
    protected _tick_label_extents(): number[];
    protected _get_factor_info(): [string[], Coords, Orient | number, Text][];
}
export declare namespace CategoricalAxis {
    interface SeparatorLine {
        separator_line_color: Color;
        separator_line_width: number;
        separator_line_alpha: number;
        separator_line_join: LineJoin;
        separator_line_cap: LineCap;
        separator_line_dash: number[];
        separator_line_dash_offset: number;
    }
    interface GroupText {
        group_text_font: string;
        group_text_font_size: string;
        group_text_font_style: FontStyle;
        group_text_color: Color;
        group_text_alpha: number;
        group_text_align: TextAlign;
        group_text_baseline: TextBaseline;
        group_text_line_height: number;
    }
    interface SubgroupText {
        subgroup_text_font: string;
        subgroup_text_font_size: string;
        subgroup_text_font_style: FontStyle;
        subgroup_text_color: Color;
        subgroup_text_alpha: number;
        subgroup_text_align: TextAlign;
        subgroup_text_baseline: TextBaseline;
        subgroup_text_line_height: number;
    }
    interface Mixins extends SeparatorLine, GroupText, SubgroupText {
    }
    interface Attrs extends Axis.Attrs, Mixins {
        ticker: CategoricalTicker;
        formatter: CategoricalTickFormatter;
        group_label_orientation: TickLabelOrientation | number;
        subgroup_label_orientation: TickLabelOrientation | number;
    }
    interface Props extends Axis.Props {
    }
    type Visuals = Axis.Visuals & {
        separator_line: Line;
        group_text: Text;
        subgroup_text: Text;
    };
}
export interface CategoricalAxis extends CategoricalAxis.Attrs {
}
export declare class CategoricalAxis extends Axis {
    properties: CategoricalAxis.Props;
    ticker: CategoricalTicker;
    formatter: CategoricalTickFormatter;
    constructor(attrs?: Partial<CategoricalAxis.Attrs>);
    static initClass(): void;
    readonly tick_coords: CategoricalTickCoords;
}
