import { Filter } from "./filter";
import { DataSource } from "../sources/data_source";
export declare namespace CustomJSFilter {
    interface Attrs extends Filter.Attrs {
        args: {
            [key: string]: any;
        };
        code: string;
        use_strict: boolean;
    }
    interface Props extends Filter.Props {
    }
}
export interface CustomJSFilter extends CustomJSFilter.Attrs {
}
export declare class CustomJSFilter extends Filter {
    properties: CustomJSFilter.Props;
    constructor(attrs?: Partial<CustomJSFilter.Attrs>);
    static initClass(): void;
    readonly names: string[];
    readonly values: any[];
    readonly func: Function;
    compute_indices(source: DataSource): number[] | null;
}
