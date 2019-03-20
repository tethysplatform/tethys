import { Constraint, Variable } from "core/layout/solver";
import * as p from "core/properties";
import { LayoutDOM, LayoutDOMView } from "./layout_dom";
export interface Rect {
    x: Variable;
    y: Variable;
    width: Variable;
    height: Variable;
}
export interface Span {
    start: Variable;
    size: Variable;
}
export interface Info {
    span: Span;
    whitespace: {
        before: Variable;
        after: Variable;
    };
}
export declare class BoxView extends LayoutDOMView {
    model: Box;
    connect_signals(): void;
    css_classes(): string[];
    get_height(): number;
    get_width(): number;
}
export declare namespace Box {
    interface Attrs extends LayoutDOM.Attrs {
        children: LayoutDOM[];
        spacing: number;
    }
    interface Props extends LayoutDOM.Props {
        children: p.Property<LayoutDOM[]>;
        spacing: p.Property<number>;
    }
}
export interface Box extends Box.Attrs {
}
export declare class Box extends LayoutDOM {
    properties: Box.Props;
    constructor(attrs?: Partial<Box.Attrs>);
    static initClass(): void;
    _horizontal: boolean;
    protected _child_equal_size_width: Variable;
    protected _child_equal_size_height: Variable;
    protected _box_equal_size_top: Variable;
    protected _box_equal_size_bottom: Variable;
    protected _box_equal_size_left: Variable;
    protected _box_equal_size_right: Variable;
    protected _box_cell_align_top: Variable;
    protected _box_cell_align_bottom: Variable;
    protected _box_cell_align_left: Variable;
    protected _box_cell_align_right: Variable;
    initialize(): void;
    get_layoutable_children(): LayoutDOM[];
    get_constrained_variables(): {
        [key: string]: Variable;
    };
    get_constraints(): Constraint[];
    protected _child_rect(vars: {
        [key: string]: Variable;
    }): Rect;
    protected _span(rect: Rect): Span;
    protected _info(vars: {
        [key: string]: Variable;
    }): Info;
    protected _flatten_cell_edge_variables(horizontal: boolean): {
        [key: string]: Variable[];
    };
    protected _align_inner_cell_edges_constraints(): Constraint[];
    protected _find_edge_leaves(horizontal: boolean): [LayoutDOM[], LayoutDOM[]];
    protected _align_outer_edges_constraints(horizontal: boolean): Constraint[];
    protected _box_insets_from_child_insets(horizontal: boolean, child_variable_prefix: string, our_variable_prefix: string, minimum: boolean): Constraint[];
    protected _box_equal_size_bounds(horizontal: boolean): Constraint[];
    protected _box_cell_align_bounds(horizontal: boolean): Constraint[];
    protected _box_whitespace(horizontal: boolean): Constraint[];
    static _left_right_inner_cell_edge_variables: string[];
    static _top_bottom_inner_cell_edge_variables: string[];
}
