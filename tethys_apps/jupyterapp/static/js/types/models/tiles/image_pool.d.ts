export declare type Image = HTMLImageElement;
export declare class ImagePool {
    protected images: Image[];
    pop(): Image;
    push(img: Image | Image[]): void;
}
