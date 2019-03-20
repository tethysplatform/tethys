import { Variable, ComputedVariable, Constraint } from "./solver";
import { HasProps } from "../has_props";
import { Arrayable } from "../types";
import { BBox } from "../util/bbox";
export interface ViewTransform {
    compute: (v: number) => number;
    v_compute: (vv: Arrayable<number>) => Arrayable<number>;
}
export declare namespace LayoutCanvas {
    interface Attrs extends HasProps.Attrs {
    }
    interface Props extends HasProps.Props {
    }
}
export interface LayoutCanvas extends LayoutCanvas.Attrs {
}
export declare abstract class LayoutCanvas extends HasProps {
    properties: LayoutCanvas.Props;
    constructor(attrs?: Partial<LayoutCanvas.Attrs>);
    static initClass(): void;
    _top: Variable;
    _left: Variable;
    _width: Variable;
    _height: Variable;
    _right: Variable;
    _bottom: Variable;
    _hcenter: ComputedVariable;
    _vcenter: ComputedVariable;
    initialize(): void;
    get_editables(): Variable[];
    get_constraints(): Constraint[];
    get_layoutable_children(): LayoutCanvas[];
    readonly bbox: BBox;
    readonly layout_bbox: {
        [key: string]: number;
    };
    readonly xview: ViewTransform;
    readonly yview: ViewTransform;
}
