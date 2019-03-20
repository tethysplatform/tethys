import { RenderItem } from "./json";
export declare const BOKEH_ROOT = "bk-root";
export declare function inject_css(url: string): void;
export declare function inject_raw_css(css: string): void;
export declare function _resolve_element(item: RenderItem): HTMLElement;
export declare function _resolve_root_elements(item: RenderItem): {
    [key: string]: HTMLElement;
};
