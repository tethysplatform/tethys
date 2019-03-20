import { MercatorTileSource } from './mercator_tile_source';
export declare namespace QUADKEYTileSource {
    interface Attrs extends MercatorTileSource.Attrs {
    }
    interface Props extends MercatorTileSource.Props {
    }
}
export interface QUADKEYTileSource extends QUADKEYTileSource.Attrs {
}
export declare class QUADKEYTileSource extends MercatorTileSource {
    properties: QUADKEYTileSource.Props;
    constructor(attrs?: Partial<QUADKEYTileSource.Attrs>);
    static initClass(): void;
    get_image_url(x: number, y: number, z: number): string;
}
