import { MercatorTileSource } from './mercator_tile_source';
export declare namespace WMTSTileSource {
    interface Attrs extends MercatorTileSource.Attrs {
    }
    interface Props extends MercatorTileSource.Props {
    }
}
export interface WMTSTileSource extends WMTSTileSource.Attrs {
}
export declare class WMTSTileSource extends MercatorTileSource {
    properties: WMTSTileSource.Props;
    constructor(attrs?: Partial<WMTSTileSource.Attrs>);
    static initClass(): void;
    get_image_url(x: number, y: number, z: number): string;
}
