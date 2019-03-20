import { Axis } from "./axis";
export declare namespace ContinuousAxis {
    interface Attrs extends Axis.Attrs {
    }
    interface Props extends Axis.Props {
    }
}
export interface ContinuousAxis extends ContinuousAxis.Attrs {
}
export declare abstract class ContinuousAxis extends Axis {
    properties: ContinuousAxis.Props;
    constructor(attrs?: Partial<ContinuousAxis.Attrs>);
    static initClass(): void;
}
