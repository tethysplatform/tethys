export interface Header {
    msgid?: string;
    msgtype?: string;
    reqid?: string;
    num_buffers?: number;
}
export declare class Message {
    readonly header: Header;
    readonly metadata: any;
    readonly content: any;
    readonly buffers: [Header, any][];
    constructor(header: Header, metadata: any, content: any);
    static assemble(header_json: string, metadata_json: string, content_json: string): Message;
    assemble_buffer(buf_header: Header, buf_payload: any): void;
    static create(msgtype: string, metadata: any, content?: any): Message;
    static create_header(msgtype: string): Header;
    complete(): boolean;
    send(socket: WebSocket): void;
    msgid(): string;
    msgtype(): string;
    reqid(): string;
    problem(): string | null;
}
