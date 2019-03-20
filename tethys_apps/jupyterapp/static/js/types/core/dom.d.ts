export declare type HTMLAttrs = {
    [name: string]: any;
};
export declare type HTMLChild = string | HTMLElement | (string | HTMLElement)[];
export declare function createElement<T extends keyof HTMLElementTagNameMap>(tag: T, attrs: HTMLAttrs, ...children: HTMLChild[]): HTMLElementTagNameMap[T];
export declare const div: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLDivElement, span: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLSpanElement, link: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLLinkElement, style: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLStyleElement, a: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLAnchorElement, p: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLParagraphElement, i: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLElement, pre: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLPreElement, button: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLButtonElement, label: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLLabelElement, input: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLInputElement, select: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLSelectElement, option: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLOptionElement, optgroup: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLOptGroupElement, textarea: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLTextAreaElement, canvas: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLCanvasElement, ul: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLUListElement, ol: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLOListElement, li: (attrs?: HTMLAttrs, ...children: HTMLChild[]) => HTMLLIElement;
export declare const nbsp: Text;
export declare function removeElement(element: HTMLElement): void;
export declare function replaceWith(element: HTMLElement, replacement: HTMLElement): void;
export declare function prepend(element: HTMLElement, ...nodes: Node[]): void;
export declare function empty(element: HTMLElement): void;
export declare function show(element: HTMLElement): void;
export declare function hide(element: HTMLElement): void;
export declare function position(element: HTMLElement): {
    top: number;
    left: number;
};
export declare function offset(element: HTMLElement): {
    top: number;
    left: number;
};
export declare function matches(el: HTMLElement, selector: string): boolean;
export declare function parent(el: HTMLElement, selector: string): HTMLElement | null;
export declare type Sizing = {
    top: number;
    bottom: number;
    left: number;
    right: number;
};
export declare function margin(el: HTMLElement): Sizing;
export declare function padding(el: HTMLElement): Sizing;
export declare enum Keys {
    Backspace = 8,
    Tab = 9,
    Enter = 13,
    Esc = 27,
    PageUp = 33,
    PageDown = 34,
    Left = 37,
    Up = 38,
    Right = 39,
    Down = 40,
    Delete = 46
}
