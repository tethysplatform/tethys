import { Message, Header } from "protocol/message";
export declare type Fragment = string | ArrayBuffer;
export declare class Receiver {
    message: Message | null;
    protected _partial: Message | null;
    protected _fragments: Fragment[];
    protected _buf_header: Header | null;
    protected _current_consumer: (fragment: Fragment) => void;
    consume(fragment: Fragment): void;
    _HEADER(fragment: Fragment): void;
    _METADATA(fragment: Fragment): void;
    _CONTENT(fragment: Fragment): void;
    _BUFFER_HEADER(fragment: Fragment): void;
    _BUFFER_PAYLOAD(fragment: Fragment): void;
    _assume_text(fragment: Fragment): void;
    _assume_binary(fragment: Fragment): void;
    _check_complete(): void;
}
