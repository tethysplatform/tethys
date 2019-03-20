import { Variable, Constraint } from "./solver";
import { LayoutCanvas } from "./layout_canvas";
import * as p from "../properties";
import { HasProps } from "../has_props";
import { DOMView } from "../dom_view";
import { Side } from "../enums";
export declare type Orient = "parallel" | "normal" | "horizontal" | "vertical";
export declare type TextOrient = "justified" | Orient;
export declare type Sizeable = {
    panel: SidePanel;
};
export declare type SizeableView = DOMView & {
    model: Sizeable;
    get_size(): number;
};
export declare function isSizeable<T extends HasProps>(model: T): model is T & Sizeable;
export declare function isSizeableView<T extends DOMView>(view: T): view is T & SizeableView;
export declare const _view_sizes: WeakMap<SizeableView, number>;
export declare const _view_constraints: WeakMap<SizeableView, Constraint>;
export declare function update_panel_constraints(view: SizeableView): void;
export declare namespace SidePanel {
    interface Attrs extends LayoutCanvas.Attrs {
        side: Side;
    }
    interface Props extends LayoutCanvas.Props {
        side: p.Property<Side>;
    }
}
export interface SidePanel extends SidePanel.Attrs {
}
export declare class SidePanel extends LayoutCanvas {
    properties: SidePanel.Props;
    constructor(attrs?: Partial<SidePanel.Attrs>);
    static initClass(): void;
    protected _dim: 0 | 1;
    protected _normals: [number, number];
    protected _size: Variable;
    toString(): string;
    initialize(): void;
    readonly dimension: 0 | 1;
    readonly normals: [number, number];
    readonly is_horizontal: boolean;
    readonly is_vertical: boolean;
    apply_label_text_heuristics(ctx: CanvasRenderingContext2D, orient: TextOrient | number): void;
    get_label_angle_heuristic(orient: Orient): number;
}
