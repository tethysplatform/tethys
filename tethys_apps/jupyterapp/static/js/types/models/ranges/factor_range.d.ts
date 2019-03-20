import { Range } from "./range";
import { PaddingUnits } from "core/enums";
import * as p from "core/properties";
import { Arrayable } from "core/types";
export declare type L1Factor = string;
export declare type L2Factor = [string, string];
export declare type L3Factor = [string, string, string];
export declare type Factor = L1Factor | L2Factor | L3Factor;
export declare type L1OffsetFactor = [string, number];
export declare type L2OffsetFactor = [string, string, number];
export declare type L3OffsetFactor = [string, string, string, number];
export declare type OffsetFactor = L1OffsetFactor | L2OffsetFactor | L3OffsetFactor;
export declare type L1Mapping = {
    [key: string]: {
        value: number;
    };
};
export declare type L2Mapping = {
    [key: string]: {
        value: number;
        mapping: L1Mapping;
    };
};
export declare type L3Mapping = {
    [key: string]: {
        value: number;
        mapping: L2Mapping;
    };
};
export declare function map_one_level(factors: L1Factor[], padding: number, offset?: number): [L1Mapping, number];
export declare function map_two_levels(factors: L2Factor[], outer_pad: number, factor_pad: number, offset?: number): [L2Mapping, string[], number];
export declare function map_three_levels(factors: L3Factor[], outer_pad: number, inner_pad: number, factor_pad: number, offset?: number): [L3Mapping, string[], [string, string][], number];
export declare namespace FactorRange {
    interface Attrs extends Range.Attrs {
        factors: Factor[];
        factor_padding: number;
        subgroup_padding: number;
        group_padding: number;
        range_padding: number;
        range_padding_units: PaddingUnits;
        start: number;
        end: number;
        levels: number;
        mids: [string, string][] | undefined;
        tops: string[] | undefined;
        tops_groups: string[];
    }
    interface Props extends Range.Props {
        factors: p.Property<Factor[]>;
        factor_padding: p.Property<number>;
        subgroup_padding: p.Property<number>;
        group_padding: p.Property<number>;
        range_padding: p.Property<number>;
        range_padding_units: p.Property<PaddingUnits>;
        start: p.Property<number>;
        end: p.Property<number>;
    }
}
export interface FactorRange extends FactorRange.Attrs {
}
export declare class FactorRange extends Range {
    properties: FactorRange.Props;
    constructor(attrs?: Partial<FactorRange.Attrs>);
    static initClass(): void;
    protected _mapping: L1Mapping | L2Mapping | L3Mapping;
    readonly min: number;
    readonly max: number;
    initialize(): void;
    connect_signals(): void;
    reset(): void;
    protected _lookup(x: any): number;
    synthetic(x: number | Factor | OffsetFactor): number;
    v_synthetic(xs: Arrayable<number | Factor | OffsetFactor>): Arrayable<number>;
    protected _init(silent: boolean): void;
}
