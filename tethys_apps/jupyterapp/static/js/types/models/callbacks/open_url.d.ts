import { Callback } from "./callback";
export declare namespace OpenURL {
    interface Attrs extends Callback.Attrs {
        url: string;
    }
    interface Props extends Callback.Props {
    }
}
export interface OpenURL extends OpenURL.Attrs {
}
export declare class OpenURL extends Callback {
    properties: OpenURL.Props;
    constructor(attrs?: Partial<OpenURL.Attrs>);
    static initClass(): void;
    execute(_cb_obj: any, cb_data: {
        [key: string]: any;
    }): any;
}
