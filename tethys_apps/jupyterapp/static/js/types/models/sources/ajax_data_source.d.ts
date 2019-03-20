import { RemoteDataSource } from "./remote_data_source";
import { UpdateMode, HTTPMethod } from "core/enums";
export declare namespace AjaxDataSource {
    interface Attrs extends RemoteDataSource.Attrs {
        mode: UpdateMode;
        content_type: string;
        http_headers: {
            [key: string]: string;
        };
        max_size: number;
        method: HTTPMethod;
        if_modified: boolean;
    }
    interface Props extends RemoteDataSource.Props {
    }
}
export interface AjaxDataSource extends AjaxDataSource.Attrs {
}
export declare class AjaxDataSource extends RemoteDataSource {
    properties: AjaxDataSource.Props;
    constructor(attrs?: Partial<AjaxDataSource.Attrs>);
    static initClass(): void;
    protected interval: number;
    protected initialized: boolean;
    destroy(): void;
    setup(): void;
    get_data(mode: UpdateMode, max_size?: number, _if_modified?: boolean): void;
    prepare_request(): XMLHttpRequest;
    do_load(xhr: XMLHttpRequest, mode: UpdateMode, max_size: number): void;
    do_error(xhr: XMLHttpRequest): void;
}
