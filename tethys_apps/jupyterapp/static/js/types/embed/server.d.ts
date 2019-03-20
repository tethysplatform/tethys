import { DOMView } from "../core/dom_view";
export declare function _get_ws_url(app_path: string | undefined, absolute_url: string | undefined): string;
export declare function add_document_from_session(websocket_url: string, session_id: string, element: HTMLElement, roots?: {
    [key: string]: HTMLElement;
}, use_for_title?: boolean): Promise<{
    [key: string]: DOMView;
}>;
