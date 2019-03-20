import { GeometryCollection, Feature, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon } from "geojson";
import { ColumnarDataSource } from "./columnar_data_source";
import * as p from "core/properties";
import { Arrayable } from "core/types";
export declare type GeoItem = Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon | GeometryCollection;
export declare type GeoData = {
    x: Arrayable<number>;
    y: Arrayable<number>;
    z: Arrayable<number>;
    xs: Arrayable<Arrayable<number>>;
    ys: Arrayable<Arrayable<number>>;
    zs: Arrayable<Arrayable<number>>;
    [key: string]: Arrayable;
};
export declare namespace GeoJSONDataSource {
    interface Attrs extends ColumnarDataSource.Attrs {
        geojson: string;
    }
    interface Props extends ColumnarDataSource.Props {
        geojson: p.Property<string>;
    }
}
export interface GeoJSONDataSource extends GeoJSONDataSource.Attrs {
}
export declare class GeoJSONDataSource extends ColumnarDataSource {
    properties: GeoJSONDataSource.Props;
    constructor(attrs?: Partial<GeoJSONDataSource.Attrs>);
    static initClass(): void;
    initialize(): void;
    connect_signals(): void;
    protected _update_data(): void;
    protected _get_new_list_array(length: number): number[][];
    protected _get_new_nan_array(length: number): number[];
    protected _add_properties(item: Feature<GeoItem>, data: GeoData, i: number, item_count: number): void;
    protected _add_geometry(geometry: GeoItem, data: GeoData, i: number): void;
    geojson_to_column_data(): GeoData;
}
