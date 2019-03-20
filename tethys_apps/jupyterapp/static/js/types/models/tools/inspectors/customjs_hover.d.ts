import { Model } from "../../../model";
export declare namespace CustomJSHover {
    interface Attrs extends Model.Attrs {
        args: {
            [key: string]: any;
        };
        code: string;
    }
    interface Props extends Model.Props {
    }
}
export interface CustomJSHover extends CustomJSHover.Attrs {
}
export declare class CustomJSHover extends Model {
    properties: CustomJSHover.Props;
    constructor(attrs?: Partial<CustomJSHover.Attrs>);
    static initClass(): void;
    readonly values: any[];
    protected _make_code(valname: string, formatname: string, varsname: string, fn: string): Function;
    format(value: any, format: string, special_vars: {
        [key: string]: any;
    }): string;
}
