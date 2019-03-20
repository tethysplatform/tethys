import { HasProps } from "../has_props";
export interface Ref {
    id: string;
    type: string;
    subtype?: string;
    attributes?: {
        [key: string]: any;
    };
}
export declare function create_ref(obj: HasProps): Ref;
export declare function is_ref(arg: any): arg is Ref;
