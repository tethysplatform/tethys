import { MercatorTileSource } from './mercator_tile_source';
export declare namespace BBoxTileSource {
    interface Attrs extends MercatorTileSource.Attrs {
        use_latlon: boolean;
    }
    interface Props extends MercatorTileSource.Props {
    }
}
export interface BBoxTileSource extends BBoxTileSource.Attrs {
}
export declare class BBoxTileSource extends MercatorTileSource {
    properties: BBoxTileSource.Props;
    constructor(attrs?: Partial<BBoxTileSource.Attrs>);
    static initClass(): void;
    get_image_url(x: number, y: number, z: number): string;
}
