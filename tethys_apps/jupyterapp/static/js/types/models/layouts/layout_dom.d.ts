import { Model } from "../../model";
import { SizingMode } from "core/enums";
import * as p from "core/properties";
import { LayoutCanvas } from "core/layout/layout_canvas";
import { Solver, Variable, Constraint } from "core/layout/solver";
import { DOMView } from "core/dom_view";
export declare type Layoutable = LayoutCanvas | LayoutDOM;
export declare abstract class LayoutDOMView extends DOMView implements EventListenerObject {
    model: LayoutDOM;
    protected _solver: Solver;
    protected _solver_inited: boolean;
    protected _idle_notified: boolean;
    protected _root_width: Variable;
    protected _root_height: Variable;
    child_views: {
        [key: string]: LayoutDOMView;
    };
    initialize(options: any): void;
    remove(): void;
    has_finished(): boolean;
    notify_finished(): void;
    protected _calc_width_height(): [number | null, number | null];
    protected _init_solver(): void;
    _suggest_dims(width: number | null, height: number | null): void;
    resize(width?: number | null, height?: number | null): void;
    partial_layout(): void;
    layout(): void;
    protected _do_layout(full: boolean, width?: number | null, height?: number | null): void;
    protected _layout(final?: boolean): void;
    rebuild_child_views(): void;
    build_child_views(): void;
    connect_signals(): void;
    handleEvent(): void;
    disconnect_signals(): void;
    _render_classes(): void;
    render(): void;
    position(): void;
    abstract get_height(): number;
    abstract get_width(): number;
    get_width_height(): [number, number];
}
export declare namespace LayoutDOM {
    interface Attrs extends Model.Attrs {
        height: number;
        width: number;
        disabled: boolean;
        sizing_mode: SizingMode;
        css_classes: string[];
    }
    interface Props extends Model.Props {
        height: p.Property<number>;
        width: p.Property<number>;
        disabled: p.Property<boolean>;
        sizing_mode: p.Property<SizingMode>;
        css_classes: p.Property<string[]>;
    }
}
export interface LayoutDOM extends LayoutDOM.Attrs {
}
export declare abstract class LayoutDOM extends Model {
    properties: LayoutDOM.Props;
    constructor(attrs?: Partial<LayoutDOM.Attrs>);
    static initClass(): void;
    _width: Variable;
    _height: Variable;
    _left: Variable;
    _right: Variable;
    _top: Variable;
    _bottom: Variable;
    _dom_top: Variable;
    _dom_left: Variable;
    _width_minus_right: Variable;
    _height_minus_bottom: Variable;
    _whitespace_top: Variable;
    _whitespace_bottom: Variable;
    _whitespace_left: Variable;
    _whitespace_right: Variable;
    initialize(): void;
    readonly layout_bbox: {
        [key: string]: number;
    };
    dump_layout(): void;
    get_all_constraints(): Constraint[];
    get_all_editables(): Variable[];
    get_constraints(): Constraint[];
    get_layoutable_children(): LayoutDOM[];
    get_editables(): Variable[];
    get_constrained_variables(): {
        [key: string]: Variable;
    };
    get_aspect_ratio(): number;
}
