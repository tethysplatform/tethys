import { Color } from "core/types";
import { FontStyle, TextAlign, RoundingFunction } from "core/enums";
import { Model } from "../../../model";
export declare namespace CellFormatter {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface CellFormatter extends CellFormatter.Attrs {
}
export declare abstract class CellFormatter extends Model {
    properties: CellFormatter.Props;
    constructor(attrs?: Partial<CellFormatter.Attrs>);
    doFormat(_row: any, _cell: any, value: any, _columnDef: any, _dataContext: any): string;
}
export declare namespace StringFormatter {
    interface Attrs extends CellFormatter.Attrs {
        font_style: FontStyle;
        text_align: TextAlign;
        text_color: Color;
    }
    interface Props extends CellFormatter.Props {
    }
}
export interface StringFormatter extends StringFormatter.Attrs {
}
export declare class StringFormatter extends CellFormatter {
    properties: StringFormatter.Props;
    constructor(attrs?: Partial<StringFormatter.Attrs>);
    static initClass(): void;
    doFormat(_row: any, _cell: any, value: any, _columnDef: any, _dataContext: any): string;
}
export declare namespace NumberFormatter {
    interface Attrs extends StringFormatter.Attrs {
        format: string;
        language: string;
        rounding: RoundingFunction;
    }
    interface Props extends StringFormatter.Props {
    }
}
export interface NumberFormatter extends NumberFormatter.Attrs {
}
export declare class NumberFormatter extends StringFormatter {
    properties: NumberFormatter.Props;
    constructor(attrs?: Partial<NumberFormatter.Attrs>);
    static initClass(): void;
    doFormat(row: any, cell: any, value: any, columnDef: any, dataContext: any): string;
}
export declare namespace BooleanFormatter {
    interface Attrs extends CellFormatter.Attrs {
        icon: string;
    }
    interface Props extends CellFormatter.Props {
    }
}
export interface BooleanFormatter extends BooleanFormatter.Attrs {
}
export declare class BooleanFormatter extends CellFormatter {
    properties: BooleanFormatter.Props;
    constructor(attrs?: Partial<BooleanFormatter.Attrs>);
    static initClass(): void;
    doFormat(_row: any, _cell: any, value: any, _columnDef: any, _dataContext: any): string;
}
export declare namespace DateFormatter {
    interface Attrs extends CellFormatter.Attrs {
        format: string;
    }
    interface Props extends CellFormatter.Props {
    }
}
export interface DateFormatter extends DateFormatter.Attrs {
}
export declare class DateFormatter extends CellFormatter {
    properties: DateFormatter.Props;
    constructor(attrs?: Partial<DateFormatter.Attrs>);
    static initClass(): void;
    getFormat(): string | undefined;
    doFormat(row: any, cell: any, value: any, columnDef: any, dataContext: any): string;
}
export declare namespace HTMLTemplateFormatter {
    interface Attrs extends CellFormatter.Attrs {
        template: string;
    }
    interface Props extends CellFormatter.Props {
    }
}
export interface HTMLTemplateFormatter extends HTMLTemplateFormatter.Attrs {
}
export declare class HTMLTemplateFormatter extends CellFormatter {
    properties: HTMLTemplateFormatter.Props;
    constructor(attrs?: Partial<HTMLTemplateFormatter.Attrs>);
    static initClass(): void;
    doFormat(_row: any, _cell: any, value: any, _columnDef: any, dataContext: any): string;
}
