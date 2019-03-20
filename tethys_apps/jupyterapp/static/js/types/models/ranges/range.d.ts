import { Model } from "../../model";
import { Plot } from "../plots/plot";
import { CustomJS } from "../callbacks/customjs";
import * as p from "core/properties";
export declare namespace Range {
    interface Attrs extends Model.Attrs {
        bounds: [number, number] | "auto" | null;
        min_interval: number;
        max_interval: number;
        callback?: ((obj: Range) => void) | CustomJS;
        plots: Plot[];
    }
    interface Props extends Model.Props {
        bounds: p.Property<[number, number] | "auto" | null>;
    }
}
export interface Range extends Range.Attrs {
}
export declare abstract class Range extends Model {
    properties: Range.Props;
    constructor(attrs?: Partial<Range.Attrs>);
    static initClass(): void;
    start: number;
    end: number;
    min: number;
    max: number;
    have_updated_interactively: boolean;
    connect_signals(): void;
    reset(): void;
    protected _emit_callback(): void;
    readonly is_reversed: boolean;
}
