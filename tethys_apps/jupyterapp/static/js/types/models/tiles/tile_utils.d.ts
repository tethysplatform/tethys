export declare function geographic_to_meters(xLon: number, yLat: number): [number, number];
export declare function meters_to_geographic(mx: number, my: number): [number, number];
export declare type Bounds = [number, number, number, number];
export declare type Extent = [number, number, number, number];
export declare function geographic_extent_to_meters(extent: Extent): Extent;
export declare function meters_extent_to_geographic(extent: Extent): Extent;
