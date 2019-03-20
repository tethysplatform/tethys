import { EllipseOval, EllipseOvalView, EllipseOvalData } from "./ellipse_oval";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
export interface EllipseData extends EllipseOvalData {
}
export interface EllipseView extends EllipseData {
}
export declare class EllipseView extends EllipseOvalView {
    model: Ellipse;
    visuals: Ellipse.Visuals;
}
export declare namespace Ellipse {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends EllipseOval.Attrs, Mixins {
    }
    interface Props extends EllipseOval.Props {
    }
    interface Visuals extends EllipseOval.Visuals {
    }
}
export interface Ellipse extends Ellipse.Attrs {
}
export declare class Ellipse extends EllipseOval {
    properties: Ellipse.Props;
    constructor(attrs?: Partial<Ellipse.Attrs>);
    static initClass(): void;
}
