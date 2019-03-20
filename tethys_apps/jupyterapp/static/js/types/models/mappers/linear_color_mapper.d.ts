import { ContinuousColorMapper } from "./continuous_color_mapper";
import { Arrayable } from "core/types";
export declare namespace LinearColorMapper {
    interface Attrs extends ContinuousColorMapper.Attrs {
    }
    interface Props extends ContinuousColorMapper.Props {
    }
}
export interface LinearColorMapper extends LinearColorMapper.Attrs {
}
export declare class LinearColorMapper extends ContinuousColorMapper {
    properties: LinearColorMapper.Props;
    constructor(attrs?: Partial<LinearColorMapper.Attrs>);
    static initClass(): void;
    protected _v_compute<T>(data: Arrayable<number>, values: Arrayable<T>, palette: Arrayable<T>, colors: {
        nan_color: T;
        low_color?: T;
        high_color?: T;
    }): void;
}
