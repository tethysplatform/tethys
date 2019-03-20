export declare const keys: (o: {}) => string[];
export declare function values<T>(object: {
    [key: string]: T;
}): T[];
export declare function extend<T1, T2>(dest: T1, src: T2): T1 & T2;
export declare function clone<T extends object>(obj: T): T;
export declare function merge<T>(obj1: {
    [key: string]: T[];
}, obj2: {
    [key: string]: T[];
}): {
    [key: string]: T[];
};
export declare function size<T>(obj: T): number;
export declare function isEmpty<T>(obj: T): boolean;
