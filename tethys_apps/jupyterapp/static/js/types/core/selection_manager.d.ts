import { HasProps } from "./has_props";
import { Geometry } from "./geometry";
import { Selection } from "models/selections/selection";
import { Renderer, RendererView } from "models/renderers/renderer";
import { ColumnarDataSource } from "models/sources/columnar_data_source";
export declare class SelectionManager extends HasProps {
    static initClass(): void;
    source: ColumnarDataSource;
    inspectors: {
        [key: string]: Selection;
    };
    initialize(): void;
    select(renderer_views: RendererView[], geometry: Geometry, final: boolean, append?: boolean): boolean;
    inspect(renderer_view: RendererView, geometry: Geometry): boolean;
    clear(rview?: RendererView): void;
    get_or_create_inspector(rmodel: Renderer): Selection;
}
