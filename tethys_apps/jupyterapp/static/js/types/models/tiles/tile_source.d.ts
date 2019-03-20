import { Model } from "../../model";
import { ImagePool } from "./image_pool";
import { Extent, Bounds } from "./tile_utils";
export interface Tile {
    tile_coords: [number, number, number];
}
export declare namespace TileSource {
    interface Attrs extends Model.Attrs {
        url: string;
        tile_size: number;
        max_zoom: number;
        min_zoom: number;
        extra_url_vars: {
            [key: string]: string;
        };
        attribution: string;
        x_origin_offset: number;
        y_origin_offset: number;
        initial_resolution: number;
    }
    interface Props extends Model.Props {
    }
}
export interface TileSource extends TileSource.Attrs {
}
export declare abstract class TileSource extends Model {
    properties: TileSource.Props;
    constructor(attrs?: Partial<TileSource.Attrs>);
    static initClass(): void;
    tiles: {
        [key: string]: Tile;
    };
    protected pool: ImagePool;
    initialize(): void;
    string_lookup_replace(str: string, lookup: {
        [key: string]: string;
    }): string;
    protected _normalize_case(): void;
    tile_xyz_to_key(x: number, y: number, z: number): string;
    key_to_tile_xyz(key: string): [number, number, number];
    sort_tiles_from_center(tiles: [number, number, number, Bounds][], tile_extent: Extent): void;
    get_image_url(x: number, y: number, z: number): string;
    abstract tile_xyz_to_quadkey(x: number, y: number, z: number): string;
    abstract quadkey_to_tile_xyz(quadkey: string): [number, number, number];
    abstract children_by_tile_xyz(x: number, y: number, z: number): [number, number, number, Bounds][];
    abstract get_closest_parent_by_tile_xyz(x: number, y: number, z: number): [number, number, number];
    abstract get_tiles_by_extent(extent: Extent, level: number, tile_border?: number): [number, number, number, Bounds][];
    abstract get_level_by_extent(extent: Extent, height: number, width: number): number;
    abstract snap_to_zoom_level(extent: Extent, height: number, width: number, level: number): Extent;
    abstract normalize_xyz(x: number, y: number, z: number): [number, number, number];
}
