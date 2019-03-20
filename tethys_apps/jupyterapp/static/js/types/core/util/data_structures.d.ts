export declare class MultiDict<T> {
    _dict: {
        [key: string]: T | T[];
    };
    _existing(key: string): T | T[] | null;
    add_value(key: string, value: T): void;
    remove_value(key: string, value: T): void;
    get_one(key: string, duplicate_error: string): T | null;
}
export declare class Set<T> {
    private _values;
    readonly values: T[];
    constructor(obj?: T[] | Set<T>);
    toString(): string;
    readonly size: number;
    has(item: T): boolean;
    add(item: T): void;
    remove(item: T): void;
    toggle(item: T): void;
    clear(): void;
    union(input: T[] | Set<T>): Set<T>;
    intersect(input: T[] | Set<T>): Set<T>;
    diff(input: T[] | Set<T>): Set<T>;
    forEach(fn: (value: T, value2: T, set: Set<T>) => void, thisArg?: any): void;
}
