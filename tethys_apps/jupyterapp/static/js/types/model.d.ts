import { HasProps } from "./core/has_props";
import { Class } from "./core/class";
import { BokehEvent } from "./core/bokeh_events";
import * as p from "./core/properties";
import { CustomJS } from "./models/callbacks/customjs";
export declare namespace Model {
    interface Attrs extends HasProps.Attrs {
        tags: string[];
        name: string | null;
        js_property_callbacks: {
            [key: string]: CustomJS[];
        };
        js_event_callbacks: {
            [key: string]: CustomJS[];
        };
        subscribed_events: string[];
    }
    interface Props extends HasProps.Props {
        tags: p.Array;
        name: p.String;
        js_property_callbacks: p.Any;
        js_event_callbacks: p.Any;
        subscribed_events: p.Array;
    }
}
export interface Model extends Model.Attrs {
}
export declare class Model extends HasProps {
    properties: Model.Props;
    constructor(attrs?: Partial<Model.Attrs>);
    static initClass(): void;
    connect_signals(): void;
    _process_event(event: BokehEvent): void;
    trigger_event(event: BokehEvent): void;
    protected _update_event_callbacks(): void;
    protected _doc_attached(): void;
    select<T extends HasProps>(selector: Class<T> | string): T[];
    select_one<T extends HasProps>(selector: Class<T> | string): T | null;
}
