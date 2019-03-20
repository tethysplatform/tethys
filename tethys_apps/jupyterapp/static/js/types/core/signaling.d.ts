import { Constructor } from "./class";
export declare type Slot<Args, Sender extends object> = ((args: Args, sender: Sender) => void) | ((args: Args) => void) | (() => void);
export declare class Signal<Args, Sender extends object> {
    readonly sender: Sender;
    readonly name: string;
    constructor(sender: Sender, name: string);
    connect(slot: Slot<Args, Sender>, context?: object | null): boolean;
    disconnect(slot: Slot<Args, Sender>, context?: object | null): boolean;
    emit(args: Args): void;
}
export declare class Signal0<Sender extends object> extends Signal<void, Sender> {
    emit(): void;
}
export declare namespace Signal {
    function disconnectBetween(sender: object, receiver: object): void;
    function disconnectSender(sender: object): void;
    function disconnectReceiver(receiver: object): void;
    function disconnectAll(obj: object): void;
}
export interface ISignalable {
    connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: Slot<Args, Sender>): boolean;
}
export declare function Signalable<C extends Constructor>(Base?: C): {
    new (): {
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: Slot<Args, Sender>): boolean;
    };
};
export declare namespace _Signalable {
    function connect<Args, Sender extends object>(this: object, signal: Signal<Args, Sender>, slot: Slot<Args, Sender>): boolean;
}
