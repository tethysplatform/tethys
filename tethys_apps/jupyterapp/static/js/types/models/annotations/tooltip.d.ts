import { Annotation, AnnotationView } from "./annotation";
import { TooltipAttachment } from "core/enums";
import * as p from "core/properties";
export declare function compute_side(attachment: TooltipAttachment, sx: number, sy: number, hcenter: number, vcenter: number): string;
export declare class TooltipView extends AnnotationView {
    model: Tooltip;
    initialize(options: any): void;
    connect_signals(): void;
    css_classes(): string[];
    render(): void;
    protected _draw_tips(): void;
}
export declare namespace Tooltip {
    interface Attrs extends Annotation.Attrs {
        attachment: TooltipAttachment;
        inner_only: boolean;
        show_arrow: boolean;
        data: [number, number, HTMLElement][];
        custom: boolean;
    }
    interface Props extends Annotation.Props {
        attachment: p.Property<TooltipAttachment>;
        inner_only: p.Property<boolean>;
        show_arrow: p.Property<boolean>;
        data: p.Property<[number, number, HTMLElement][]>;
        custom: p.Property<boolean>;
    }
}
export interface Tooltip extends Tooltip.Attrs {
}
export declare class Tooltip extends Annotation {
    properties: Tooltip.Props;
    constructor(attrs?: Partial<Tooltip.Attrs>);
    static initClass(): void;
    clear(): void;
    add(sx: number, sy: number, content: HTMLElement): void;
}
