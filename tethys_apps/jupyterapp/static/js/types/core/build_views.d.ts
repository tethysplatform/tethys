import { HasProps } from "./has_props";
import { View } from "./view";
import { Class } from "./class";
export declare type ViewStorage = {
    [key: string]: View;
};
export declare function build_views<T extends HasProps>(view_storage: ViewStorage, models: T[], options: object, cls?: (model: T) => Class<View>): View[];
export declare function remove_views(view_storage: ViewStorage): void;
