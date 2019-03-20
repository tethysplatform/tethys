import { Box, BoxView, BoxData } from "./box";
import { Arrayable } from "core/types";
import { NumberSpec } from "core/vectorization";
import { Anchor } from "core/enums";
import { SpatialIndex } from "core/util/spatial";
export interface QuadData extends BoxData {
    _right: Arrayable<number>;
    _bottom: Arrayable<number>;
    _left: Arrayable<number>;
    _top: Arrayable<number>;
    sright: Arrayable<number>;
    sbottom: Arrayable<number>;
    sleft: Arrayable<number>;
    stop: Arrayable<number>;
}
export interface QuadView extends QuadData {
}
export declare class QuadView extends BoxView {
    model: Quad;
    visuals: Quad.Visuals;
    get_anchor_point(anchor: Anchor, i: number, _spt: [number, number]): {
        x: number;
        y: number;
    } | null;
    scenterx(i: number): number;
    scentery(i: number): number;
    protected _index_data(): SpatialIndex;
    protected _lrtb(i: number): [number, number, number, number];
}
export declare namespace Quad {
    interface Attrs extends Box.Attrs {
        right: NumberSpec;
        bottom: NumberSpec;
        left: NumberSpec;
        top: NumberSpec;
    }
    interface Props extends Box.Props {
    }
    interface Visuals extends Box.Visuals {
    }
}
export interface Quad extends Quad.Attrs {
}
export declare class Quad extends Box {
    properties: Quad.Props;
    constructor(attrs?: Partial<Quad.Attrs>);
    static initClass(): void;
}
