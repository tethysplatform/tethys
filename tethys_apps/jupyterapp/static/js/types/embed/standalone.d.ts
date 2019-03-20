import { Document } from "../document";
import { DOMView } from "../core/dom_view";
export declare function add_document_standalone(document: Document, element: HTMLElement, roots?: {
    [key: string]: HTMLElement;
}, use_for_title?: boolean): {
    [key: string]: DOMView;
};
