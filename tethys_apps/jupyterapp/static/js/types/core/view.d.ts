import { HasProps } from "./has_props";
import { Signal0, Signal } from "./signaling";
export interface ViewOptions {
    id?: string;
    model?: HasProps;
    parent: View | null;
    connect_signals?: boolean;
}
declare const View_base: {
    new (): {
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class View extends View_base {
    readonly removed: Signal0<this>;
    readonly id: string;
    readonly model: HasProps;
    private _parent;
    constructor(options: ViewOptions);
    initialize(_options: ViewOptions): void;
    remove(): void;
    toString(): string;
    readonly parent: View | null;
    readonly is_root: boolean;
    readonly root: View;
    connect_signals(): void;
    disconnect_signals(): void;
    notify_finished(): void;
}
export {};
