import { EventManager } from "document";
import { Message } from "protocol/message";
import { ClientConnection } from "./connection";
export declare class ClientSession {
    protected readonly _connection: ClientConnection;
    readonly document: any;
    readonly id: string;
    protected _document_listener: (event: any) => void;
    readonly event_manager: EventManager;
    constructor(_connection: ClientConnection, document: any, id: string);
    handle(message: Message): void;
    close(): void;
    send_event(event: any): void;
    _connection_closed(): void;
    request_server_info(): Promise<any>;
    force_roundtrip(): Promise<undefined>;
    protected _document_changed(event: any): void;
    protected _handle_patch(message: Message): void;
    protected _handle_ok(message: Message): void;
    protected _handle_error(message: Message): void;
}
