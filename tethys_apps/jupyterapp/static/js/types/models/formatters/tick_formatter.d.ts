import { Model } from "../../model";
import { Axis } from "../axes/axis";
export declare namespace TickFormatter {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface TickFormatter extends TickFormatter.Attrs {
}
export declare abstract class TickFormatter extends Model {
    constructor(attrs?: Partial<TickFormatter.Attrs>);
    static initClass(): void;
    abstract doFormat(ticks: string[] | number[], axis: Axis): string[];
}
