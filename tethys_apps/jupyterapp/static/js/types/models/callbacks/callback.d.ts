import { Model } from "../../model";
export declare namespace Callback {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface Callback extends Callback.Attrs {
}
export declare abstract class Callback extends Model {
    properties: Callback.Props;
    constructor(attrs?: Partial<Callback.Attrs>);
    static initClass(): void;
    abstract execute(cb_obj: any, cb_data: {
        [key: string]: any;
    }): any;
}
