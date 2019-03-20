import { EllipseOval, EllipseOvalView, EllipseOvalData } from "./ellipse_oval";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
export interface OvalData extends EllipseOvalData {
}
export interface OvalView extends OvalData {
}
export declare class OvalView extends EllipseOvalView {
    model: Oval;
    visuals: Oval.Visuals;
    protected _map_data(): void;
}
export declare namespace Oval {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends EllipseOval.Attrs, Mixins {
    }
    interface Props extends EllipseOval.Props {
    }
    interface Visuals extends EllipseOval.Visuals {
    }
}
export interface Oval extends Oval.Attrs {
}
export declare class Oval extends EllipseOval {
    properties: Oval.Props;
    constructor(attrs?: Partial<Oval.Attrs>);
    static initClass(): void;
}
