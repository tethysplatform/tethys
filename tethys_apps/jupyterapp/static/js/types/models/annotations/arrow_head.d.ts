import { Annotation } from "./annotation";
import { Visuals, Line, Fill } from "core/visuals";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import * as p from "core/properties";
import { Context2d } from "core/util/canvas";
export declare namespace ArrowHead {
    interface Attrs extends Annotation.Attrs {
        size: number;
    }
    interface Props extends Annotation.Props {
        size: p.Property<number>;
    }
}
export interface ArrowHead extends ArrowHead.Attrs {
}
export declare abstract class ArrowHead extends Annotation {
    constructor(attrs?: Partial<ArrowHead.Attrs>);
    static initClass(): void;
    visuals: Visuals;
    initialize(): void;
    abstract render(ctx: Context2d, i: number): void;
    abstract clip(ctx: Context2d, i: number): void;
}
export declare namespace OpenHead {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends ArrowHead.Attrs, Mixins {
    }
    interface Props extends ArrowHead.Props {
    }
}
export interface OpenHead extends OpenHead.Attrs {
}
export declare class OpenHead extends ArrowHead {
    properties: OpenHead.Props;
    constructor(attrs?: Partial<OpenHead.Attrs>);
    static initClass(): void;
    visuals: Visuals & {
        line: Line;
    };
    clip(ctx: Context2d, i: number): void;
    render(ctx: Context2d, i: number): void;
}
export declare namespace NormalHead {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends ArrowHead.Attrs, Mixins {
    }
    interface Props extends ArrowHead.Props {
    }
}
export interface NormalHead extends NormalHead.Attrs {
}
export declare class NormalHead extends ArrowHead {
    properties: NormalHead.Props;
    constructor(attrs?: Partial<NormalHead.Attrs>);
    static initClass(): void;
    visuals: Visuals & {
        line: Line;
        fill: Fill;
    };
    clip(ctx: Context2d, i: number): void;
    render(ctx: Context2d, i: number): void;
    _normal(ctx: Context2d, _i: number): void;
}
export declare namespace VeeHead {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends ArrowHead.Attrs, Mixins {
    }
    interface Props extends ArrowHead.Props {
    }
}
export interface VeeHead extends VeeHead.Attrs {
}
export declare class VeeHead extends ArrowHead {
    properties: VeeHead.Props;
    constructor(attrs?: Partial<VeeHead.Attrs>);
    static initClass(): void;
    visuals: Visuals & {
        line: Line;
        fill: Fill;
    };
    clip(ctx: Context2d, i: number): void;
    render(ctx: Context2d, i: number): void;
    _vee(ctx: Context2d, _i: number): void;
}
export declare namespace TeeHead {
    interface Mixins extends LineMixinVector {
    }
    interface Attrs extends ArrowHead.Attrs, Mixins {
    }
    interface Props extends ArrowHead.Props {
    }
}
export interface TeeHead extends TeeHead.Attrs {
}
export declare class TeeHead extends ArrowHead {
    properties: TeeHead.Props;
    constructor(attrs?: Partial<TeeHead.Attrs>);
    static initClass(): void;
    visuals: Visuals & {
        line: Line;
    };
    render(ctx: Context2d, i: number): void;
    clip(_ctx: Context2d, _i: number): void;
}
