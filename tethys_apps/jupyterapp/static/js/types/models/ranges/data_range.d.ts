import { Range } from "./range";
import { Renderer } from "../renderers/renderer";
export declare namespace DataRange {
    interface Attrs extends Range.Attrs {
        names: string[];
        renderers: Renderer[];
    }
    interface Props extends Range.Props {
    }
}
export interface DataRange extends DataRange.Attrs {
}
export declare abstract class DataRange extends Range {
    properties: DataRange.Props;
    constructor(attrs?: Partial<DataRange.Attrs>);
    static initClass(): void;
}
