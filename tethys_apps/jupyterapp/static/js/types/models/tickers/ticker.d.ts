import { Model } from "../../model";
export declare type TickSpec<T> = {
    major: T[];
    minor: T[];
};
export declare namespace Ticker {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface Ticker<T> extends Ticker.Attrs {
}
export declare abstract class Ticker<T> extends Model {
    properties: Ticker.Props;
    constructor(attrs?: Partial<Ticker.Attrs>);
    static initClass(): void;
    abstract get_ticks(data_low: number, data_high: number, range: any, cross_loc: any, unused: any): TickSpec<T>;
}
