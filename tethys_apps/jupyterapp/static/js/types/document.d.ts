import { HasProps } from "./core/has_props";
import { Signal0 } from "./core/signaling";
import { Ref } from "./core/util/refs";
import { MultiDict, Set } from "./core/util/data_structures";
import { LayoutDOM } from "./models/layouts/layout_dom";
import { Index } from "./models/sources/column_data_source";
import { ClientSession } from "./client/session";
import { Model } from "./model";
export declare class EventManager {
    readonly document: any;
    session: ClientSession | null;
    subscribed_models: Set<string>;
    constructor(document: any);
    send_event(event: any): void;
    trigger(event: any): void;
}
export interface DocJson {
    version?: string;
    title?: string;
    roots: {
        root_ids: string[];
        references: Ref[];
    };
}
export interface ModelChanged {
    kind: "ModelChanged";
    model: Ref;
    attr: string;
    new: any;
}
export interface TitleChanged {
    kind: "TitleChanged";
    title: string;
}
export interface RootAdded {
    kind: "RootAdded";
    model: Ref;
}
export interface RootRemoved {
    kind: "RootRemoved";
    model: Ref;
}
export interface ColumnDataChanged {
    kind: "ColumnDataChanged";
    column_source: Ref;
    cols?: any;
    new: any;
}
export interface ColumnsStreamed {
    kind: "ColumnsStreamed";
    column_source: Ref;
    data: {
        [key: string]: any[];
    };
    rollover?: number;
}
export interface ColumnsPatched {
    kind: "ColumnsPatched";
    column_source: Ref;
    patches: {
        [key: string]: [Index, any][];
    };
}
export declare type DocumentChanged = ModelChanged | TitleChanged | RootAdded | RootRemoved | ColumnDataChanged | ColumnsStreamed | ColumnsPatched;
export interface Patch {
    references: Ref[];
    events: DocumentChanged[];
}
export declare type Attrs = {
    [key: string]: any;
};
export declare type References = {
    [key: string]: HasProps;
};
export declare abstract class DocumentChangedEvent {
    readonly document: Document;
    constructor(document: Document);
    abstract json(references: References): DocumentChanged;
}
export declare class ModelChangedEvent extends DocumentChangedEvent {
    readonly model: HasProps;
    readonly attr: string;
    readonly old: any;
    readonly new_: any;
    readonly setter_id?: string | undefined;
    constructor(document: Document, model: HasProps, attr: string, old: any, new_: any, setter_id?: string | undefined);
    json(references: References): ModelChanged;
}
export declare class TitleChangedEvent extends DocumentChangedEvent {
    readonly title: string;
    readonly setter_id?: string | undefined;
    constructor(document: Document, title: string, setter_id?: string | undefined);
    json(_references: References): TitleChanged;
}
export declare class RootAddedEvent extends DocumentChangedEvent {
    readonly model: HasProps;
    readonly setter_id?: string | undefined;
    constructor(document: Document, model: HasProps, setter_id?: string | undefined);
    json(references: References): RootAdded;
}
export declare class RootRemovedEvent extends DocumentChangedEvent {
    readonly model: HasProps;
    readonly setter_id?: string | undefined;
    constructor(document: Document, model: HasProps, setter_id?: string | undefined);
    json(_references: References): RootRemoved;
}
export declare const documents: Document[];
export declare const DEFAULT_TITLE = "Bokeh Application";
export declare class Document {
    readonly event_manager: EventManager;
    readonly idle: Signal0<this>;
    protected readonly _init_timestamp: number;
    protected _title: string;
    protected _roots: Model[];
    protected _all_models: {
        [key: string]: HasProps;
    };
    protected _all_models_by_name: MultiDict<HasProps>;
    protected _all_models_freeze_count: number;
    protected _callbacks: any[];
    protected _idle_roots: WeakMap<Model, boolean>;
    protected _interactive_timestamp: number | null;
    protected _interactive_plot: Model | null;
    constructor();
    readonly layoutables: LayoutDOM[];
    readonly is_idle: boolean;
    notify_idle(model: Model): void;
    clear(): void;
    interactive_start(plot: Model): void;
    interactive_stop(plot: Model): void;
    interactive_duration(): number;
    destructively_move(dest_doc: Document): void;
    protected _push_all_models_freeze(): void;
    protected _pop_all_models_freeze(): void;
    _invalidate_all_models(): void;
    protected _recompute_all_models(): void;
    roots(): Model[];
    add_root(model: Model, setter_id?: string): void;
    remove_root(model: Model, setter_id?: string): void;
    title(): string;
    set_title(title: string, setter_id?: string): void;
    get_model_by_id(model_id: string): HasProps | null;
    get_model_by_name(name: string): HasProps | null;
    on_change(callback: any): void;
    remove_on_change(callback: any): void;
    _trigger_on_change(event: any): void;
    _notify_change(model: HasProps, attr: string, old: any, new_: any, options?: {
        setter_id?: string;
    }): void;
    static _references_json(references: HasProps[], include_defaults?: boolean): Ref[];
    static _instantiate_object(obj_id: string, obj_type: string, obj_attrs: {
        [key: string]: any;
    }): HasProps;
    static _instantiate_references_json(references_json: Ref[], existing_models: {
        [key: string]: HasProps;
    }): References;
    static _resolve_refs(value: any, old_references: References, new_references: References): any;
    static _initialize_references_json(references_json: Ref[], old_references: References, new_references: References): void;
    static _event_for_attribute_change(changed_obj: Ref, key: string, new_value: any, doc: Document, value_refs: {
        [key: string]: HasProps;
    }): ModelChanged | null;
    static _events_to_sync_objects(from_obj: Ref, to_obj: Ref, to_doc: Document, value_refs: {
        [key: string]: HasProps;
    }): ModelChanged[];
    static _compute_patch_since_json(from_json: DocJson, to_doc: Document): Patch;
    to_json_string(include_defaults?: boolean): string;
    to_json(include_defaults?: boolean): DocJson;
    static from_json_string(s: string): Document;
    static from_json(json: DocJson): Document;
    replace_with_json(json: DocJson): void;
    create_json_patch_string(events: DocumentChangedEvent[]): string;
    create_json_patch(events: DocumentChangedEvent[]): Patch;
    apply_json_patch(patch: Patch, buffers: [any, any][], setter_id?: string): void;
}
