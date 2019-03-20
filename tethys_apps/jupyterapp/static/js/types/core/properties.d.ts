import { Signal0, Signal } from "./signaling";
import { HasProps } from "./has_props";
import * as enums from "./enums";
import { Arrayable } from "./types";
import { ColumnarDataSource } from "../models/sources/columnar_data_source";
export declare function isSpec(obj: any): boolean;
declare const Property_base: {
    new (): {
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Property<T> extends Property_base {
    readonly obj: HasProps;
    readonly attr: string;
    readonly default_value?: ((obj: HasProps) => T) | undefined;
    spec: {
        value?: any;
        field?: string;
        expr?: any;
        transform?: any;
        units?: any;
    };
    optional: boolean;
    dataspec: boolean;
    readonly change: Signal0<HasProps>;
    constructor(obj: HasProps, attr: string, default_value?: ((obj: HasProps) => T) | undefined);
    update(): void;
    init(): void;
    transform(values: any): any;
    validate(_value: any): void;
    value(do_spec_transform?: boolean): any;
    array(source: ColumnarDataSource): any[];
    _init(): void;
    toString(): string;
}
export declare function simple_prop<T>(name: string, pred: (value: any) => boolean): {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => T) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => T) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
declare const Any_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Any extends Any_base {
}
declare const Array_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Array extends Array_base {
}
declare const Bool_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Bool extends Bool_base {
}
export declare const Boolean: typeof Bool;
declare const Color_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Color extends Color_base {
}
declare const Instance_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Instance extends Instance_base {
}
declare const Number_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Number extends Number_base {
}
export declare const Int: typeof Number;
declare const Percent_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Percent extends Percent_base {
}
declare const String_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class String extends String_base {
}
export declare class Font extends String {
}
export declare function enum_prop<T>(name: string, enum_values: T[]): {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
declare const Anchor_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Anchor extends Anchor_base {
}
declare const AngleUnits_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class AngleUnits extends AngleUnits_base {
}
declare const Direction_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Direction extends Direction_base {
    transform(values: any): any;
}
declare const Dimension_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Dimension extends Dimension_base {
}
declare const Dimensions_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Dimensions extends Dimensions_base {
}
declare const FontStyle_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class FontStyle extends FontStyle_base {
}
declare const LatLon_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class LatLon extends LatLon_base {
}
declare const LineCap_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class LineCap extends LineCap_base {
}
declare const LineJoin_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class LineJoin extends LineJoin_base {
}
declare const LegendLocation_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class LegendLocation extends LegendLocation_base {
}
declare const Location_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Location extends Location_base {
}
declare const OutputBackend_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class OutputBackend extends OutputBackend_base {
}
declare const Orientation_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Orientation extends Orientation_base {
}
declare const VerticalAlign_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class VerticalAlign extends VerticalAlign_base {
}
declare const TextAlign_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class TextAlign extends TextAlign_base {
}
declare const TextBaseline_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class TextBaseline extends TextBaseline_base {
}
declare const RenderLevel_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class RenderLevel extends RenderLevel_base {
}
declare const RenderMode_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class RenderMode extends RenderMode_base {
}
declare const SizingMode_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class SizingMode extends SizingMode_base {
}
declare const SpatialUnits_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class SpatialUnits extends SpatialUnits_base {
}
declare const Distribution_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Distribution extends Distribution_base {
}
declare const StepMode_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class StepMode extends StepMode_base {
}
declare const PaddingUnits_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class PaddingUnits extends PaddingUnits_base {
}
declare const StartEnd_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        init(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class StartEnd extends StartEnd_base {
}
export declare function units_prop<Units>(name: string, valid_units: Units[], default_units: any): {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        init(): void;
        units: Units;
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
declare const Angle_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        init(): void;
        units: enums.AngleUnits;
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Angle extends Angle_base {
    transform(values: Arrayable): Arrayable;
}
declare const Distance_base: {
    new (obj: HasProps, attr: string, default_value?: ((obj: HasProps) => {}) | undefined): {
        init(): void;
        units: enums.SpatialUnits;
        validate(value: any): void;
        spec: {
            value?: any;
            field?: string | undefined;
            expr?: any;
            transform?: any;
            units?: any;
        };
        optional: boolean;
        dataspec: boolean;
        readonly change: Signal0<HasProps>;
        readonly obj: HasProps;
        readonly attr: string;
        readonly default_value?: ((obj: HasProps) => {}) | undefined;
        update(): void;
        transform(values: any): any;
        value(do_spec_transform?: boolean): any;
        array(source: ColumnarDataSource): any[];
        _init(): void;
        toString(): string;
        connect<Args, Sender extends object>(signal: Signal<Args, Sender>, slot: import("core/signaling").Slot<Args, Sender>): boolean;
    };
};
export declare class Distance extends Distance_base {
}
export declare class AngleSpec extends Angle {
}
export declare class ColorSpec extends Color {
}
export declare class DistanceSpec extends Distance {
}
export declare class FontSizeSpec extends String {
}
export declare class MarkerSpec extends String {
}
export declare class NumberSpec extends Number {
}
export declare class StringSpec extends String {
}
export {};
