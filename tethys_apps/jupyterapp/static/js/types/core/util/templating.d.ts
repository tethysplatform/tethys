import { Anything } from "../types";
import { ColumnarDataSource } from "models/sources/columnar_data_source";
import { ImageIndex } from "../../models/glyphs/image";
import { CustomJSHover } from 'models/tools/inspectors/customjs_hover';
export declare type FormatterType = "numeral" | "printf" | "datetime";
export declare type FormatterSpec = CustomJSHover | FormatterType;
export declare type Formatters = {
    [key: string]: FormatterSpec;
};
export declare type FormatterFunc = (value: any, format: string, special_vars: Vars) => string;
export declare type Index = number | ImageIndex;
export declare type Vars = {
    [key: string]: Anything;
};
export declare const DEFAULT_FORMATTERS: {
    numeral: (value: any, format: string, _special_vars: Vars) => string;
    datetime: (value: any, format: string, _special_vars: Vars) => string;
    printf: (value: any, format: string, _special_vars: Vars) => string;
};
export declare function basic_formatter(value: any, _format: string, _special_vars: Vars): string;
export declare function get_formatter(name: string, raw_spec: string, format?: string, formatters?: Formatters): FormatterFunc;
export declare function get_value(name: string, data_source: ColumnarDataSource, i: Index, special_vars: Vars): any;
export declare function replace_placeholders(str: string, data_source: ColumnarDataSource, i: Index, formatters?: Formatters, special_vars?: Vars): string;
