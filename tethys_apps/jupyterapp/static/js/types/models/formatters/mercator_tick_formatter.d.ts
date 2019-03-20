import { BasicTickFormatter } from "./basic_tick_formatter";
import { Axis } from "../axes/axis";
import { LatLon } from "core/enums";
export declare namespace MercatorTickFormatter {
    interface Attrs extends BasicTickFormatter.Attrs {
        dimension: LatLon;
    }
    interface Props extends BasicTickFormatter.Props {
    }
}
export interface MercatorTickFormatter extends MercatorTickFormatter.Attrs {
}
export declare class MercatorTickFormatter extends BasicTickFormatter {
    properties: MercatorTickFormatter.Props;
    constructor(attrs?: Partial<MercatorTickFormatter.Attrs>);
    static initClass(): void;
    doFormat(ticks: number[], axis: Axis): string[];
}
