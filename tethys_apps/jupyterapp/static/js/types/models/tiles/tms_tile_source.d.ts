import { MercatorTileSource } from './mercator_tile_source';
export declare namespace TMSTileSource {
    interface Attrs extends MercatorTileSource.Attrs {
    }
    interface Props extends MercatorTileSource.Props {
    }
}
export interface TMSTileSource extends TMSTileSource.Attrs {
}
export declare class TMSTileSource extends MercatorTileSource {
    properties: TMSTileSource.Props;
    constructor(attrs?: Partial<TMSTileSource.Attrs>);
    static initClass(): void;
    get_image_url(x: number, y: number, z: number): string;
}
