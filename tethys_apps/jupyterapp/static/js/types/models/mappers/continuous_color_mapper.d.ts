import { ColorMapper } from "./color_mapper";
import { Arrayable, Color } from "core/types";
export declare namespace ContinuousColorMapper {
    interface Attrs extends ColorMapper.Attrs {
        high: number;
        low: number;
        high_color: Color;
        low_color: Color;
    }
    interface Props extends ColorMapper.Props {
    }
}
export interface ContinuousColorMapper extends ContinuousColorMapper.Attrs {
}
export declare abstract class ContinuousColorMapper extends ColorMapper {
    properties: ContinuousColorMapper.Props;
    constructor(attrs?: Partial<ContinuousColorMapper.Attrs>);
    static initClass(): void;
    protected _colors<T>(conv: (c: Color) => T): {
        nan_color: T;
        low_color?: T;
        high_color?: T;
    };
    protected abstract _v_compute<T>(data: Arrayable<number>, values: Arrayable<T>, palette: Arrayable<T>, colors: {
        nan_color: T;
        low_color?: T;
        high_color?: T;
    }): void;
}
