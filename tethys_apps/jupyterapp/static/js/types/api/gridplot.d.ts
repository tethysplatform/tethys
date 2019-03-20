import { LayoutDOM } from "./models";
import { SizingMode, Location } from "../core/enums";
export interface GridPlotOpts {
    toolbar_location?: Location | null;
    sizing_mode?: SizingMode;
    merge_tools?: boolean;
}
export declare function gridplot(children: (LayoutDOM | null)[][], opts?: GridPlotOpts): LayoutDOM;
