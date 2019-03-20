import { Callback } from "./callback";
export declare namespace CustomJS {
    interface Attrs extends Callback.Attrs {
        args: {
            [key: string]: any;
        };
        code: string;
        use_strict: boolean;
    }
    interface Props extends Callback.Props {
    }
}
export interface CustomJS extends CustomJS.Attrs {
}
export declare class CustomJS extends Callback {
    properties: CustomJS.Props;
    constructor(attrs?: Partial<CustomJS.Attrs>);
    static initClass(): void;
    readonly names: string[];
    readonly values: any[];
    readonly func: Function;
    execute(cb_obj: any, cb_data: {
        [key: string]: any;
    }): any;
}
