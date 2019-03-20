import { View } from "./view";
import { Class } from "./class";
import { Signal0, Signal } from "./signaling";
import { Ref } from "./util/refs";
import * as p from "./properties";
import { Property } from "./properties";
import { ColumnarDataSource } from "models/sources/columnar_data_source";
import { Document } from "../document";
export declare module HasProps {
    interface Attrs {
        id: string;
    }
    interface Props {
        id: p.Any;
    }
    interface SetOptions {
        check_eq?: boolean;
        silent?: boolean;
        no_change?: boolean;
        defaults?: boolean;
        setter_id?: string;
    }
}
export interface HasProps extends HasProps.Attrs {
}
declare const HasProps_base: {
    new (): {
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare abstract class HasProps extends HasProps_base {
    static initClass(): void;
    type: string;
    default_view: Class<View>;
    props: {
        [key: string]: {
            type: Class<Property<any>>;
            default_value: any;
            internal: boolean;
        };
    };
    mixins: string[];
    private static _fix_default;
    static define(obj: any): void;
    static internal(obj: any): void;
    static mixin(...names: string[]): void;
    static mixins(names: string[]): void;
    static override(obj: any): void;
    toString(): string;
    _subtype: string | undefined;
    document: Document | null;
    readonly destroyed: Signal0<this>;
    readonly change: Signal0<this>;
    readonly transformchange: Signal0<this>;
    readonly attributes: {
        [key: string]: any;
    };
    readonly properties: {
        [key: string]: any;
    };
    protected readonly _set_after_defaults: {
        [key: string]: boolean;
    };
    constructor(attrs?: {
        [key: string]: any;
    });
    finalize(): void;
    initialize(): void;
    connect_signals(): void;
    disconnect_signals(): void;
    destroy(): void;
    clone(): this;
    private _pending;
    private _changing;
    private _setv;
    setv(attrs: {
        [key: string]: any;
    }, options?: HasProps.SetOptions): void;
    getv(prop_name: string): any;
    ref(): Ref;
    set_subtype(subtype: string): void;
    attribute_is_serializable(attr: string): boolean;
    serializable_attributes(): {
        [key: string]: any;
    };
    static _value_to_json(_key: string, value: any, _optional_parent_object: any): any;
    attributes_as_json(include_defaults?: boolean, value_to_json?: typeof HasProps._value_to_json): any;
    static _json_record_references(doc: Document, v: any, result: {
        [key: string]: HasProps;
    }, recurse: boolean): void;
    static _value_record_references(v: any, result: {
        [key: string]: HasProps;
    }, recurse: boolean): void;
    protected _immediate_references(): HasProps[];
    references(): HasProps[];
    protected _doc_attached(): void;
    attach_document(doc: Document): void;
    detach_document(): void;
    protected _tell_document_about_change(attr: string, old: any, new_: any, options: {
        setter_id?: string;
    }): void;
    materialize_dataspecs(source: ColumnarDataSource): {
        [key: string]: any;
    };
}
export {};
