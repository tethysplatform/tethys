import { ContinuousColorMapper } from "./continuous_color_mapper";
import { Arrayable } from "core/types";
export declare namespace LogColorMapper {
    interface Attrs extends ContinuousColorMapper.Attrs {
    }
    interface Props extends ContinuousColorMapper.Props {
    }
}
export interface LogColorMapper extends LogColorMapper.Attrs {
}
export declare class LogColorMapper extends ContinuousColorMapper {
    properties: LogColorMapper.Props;
    constructor(attrs?: Partial<LogColorMapper.Attrs>);
    static initClass(): void;
    protected _v_compute<T>(data: Arrayable<number>, values: Arrayable<T>, palette: Arrayable<T>, colors: {
        nan_color: T;
        low_color?: T;
        high_color?: T;
    }): void;
}
