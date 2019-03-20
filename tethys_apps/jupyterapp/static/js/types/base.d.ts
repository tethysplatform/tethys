import { HasProps } from "./core/has_props";
import { Class } from "./core/class";
export declare type View = any;
export declare const overrides: {
    [key: string]: Class<HasProps>;
};
export interface Models {
    (name: string): Class<HasProps>;
    register(name: string, model: Class<HasProps>): void;
    unregister(name: string): void;
    register_models(models: {
        [key: string]: Class<HasProps>;
    } | null | undefined, force?: boolean, errorFn?: (name: string) => void): void;
    registered_names(): string[];
}
export declare const Models: Models;
export declare const register_models: (models: {
    [key: string]: Class<HasProps>;
} | null | undefined, force?: boolean | undefined, errorFn?: ((name: string) => void) | undefined) => void;
export declare const index: {
    [key: string]: View;
};
