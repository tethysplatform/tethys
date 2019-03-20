export interface Class<T> {
    new (...args: any[]): T;
    prototype: T;
}
export declare type Constructor<T = {}> = new (...args: any[]) => T;
