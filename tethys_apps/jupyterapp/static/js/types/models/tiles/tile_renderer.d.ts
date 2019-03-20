import { ImagePool, Image } from "./image_pool";
import { Extent, Bounds } from "./tile_utils";
import { TileSource } from "./tile_source";
import { Renderer, RendererView } from "../renderers/renderer";
export interface TileData {
    img: Image;
    tile_coords: [number, number, number];
    normalized_coords: [number, number, number];
    quadkey: string;
    cache_key: string;
    bounds: Bounds;
    loaded: boolean;
    finished: boolean;
    x_coord: number;
    y_coord: number;
}
export declare class TileRendererView extends RendererView {
    model: TileRenderer;
    protected attributionEl: HTMLElement | null;
    protected _tiles: TileData[];
    protected pool: ImagePool;
    protected extent: Extent;
    protected initial_extent: Extent;
    protected _last_height?: number;
    protected _last_width?: number;
    protected map_initialized?: boolean;
    protected render_timer?: number;
    protected prefetch_timer?: number;
    initialize(options: any): void;
    connect_signals(): void;
    get_extent(): Extent;
    private readonly map_plot;
    private readonly map_canvas;
    private readonly map_frame;
    private readonly x_range;
    private readonly y_range;
    protected _set_data(): void;
    protected _add_attribution(): void;
    protected _map_data(): void;
    protected _on_tile_load(tile_data: TileData, e: Event & {
        target: Image;
    }): void;
    protected _on_tile_cache_load(tile_data: TileData, e: Event & {
        target: Image;
    }): void;
    protected _on_tile_error(tile_data: TileData): void;
    protected _create_tile(x: number, y: number, z: number, bounds: Bounds, cache_only?: boolean): void;
    protected _enforce_aspect_ratio(): void;
    has_finished(): boolean;
    render(): void;
    _draw_tile(tile_key: string): void;
    protected _set_rect(): void;
    protected _render_tiles(tile_keys: string[]): void;
    protected _prefetch_tiles(): void;
    protected _fetch_tiles(tiles: [number, number, number, Bounds][]): void;
    protected _update(): void;
}
export declare namespace TileRenderer {
    interface Attrs extends Renderer.Attrs {
        alpha: number;
        x_range_name: string;
        y_range_name: string;
        smoothing: boolean;
        tile_source: TileSource;
        render_parents: boolean;
    }
    interface Props extends Renderer.Props {
    }
}
export interface TileRenderer extends TileRenderer.Attrs {
}
export declare class TileRenderer extends Renderer {
    properties: TileRenderer.Props;
    constructor(attrs?: Partial<TileRenderer.Attrs>);
    static initClass(): void;
}
