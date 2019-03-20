export declare type Rect = {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
};
export declare type IndexedRect = Rect & {
    i: number;
};
export declare class SpatialIndex {
    private readonly points;
    private readonly index;
    constructor(points: IndexedRect[]);
    readonly bbox: Rect;
    search(rect: Rect): IndexedRect[];
    indices(rect: Rect): number[];
}
