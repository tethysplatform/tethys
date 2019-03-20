import { DOMView } from "core/dom_view";
import { Model } from "../../../model";
import { Item } from "./data_table";
export declare abstract class CellEditorView extends DOMView {
    model: CellEditor;
    defaultValue: any;
    readonly emptyValue: any;
    inputEl: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
    protected args: any;
    protected abstract _createInput(): HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
    constructor(options: any);
    initialize(options: any): void;
    css_classes(): string[];
    render(): void;
    renderEditor(): void;
    disableNavigation(): void;
    destroy(): void;
    focus(): void;
    show(): void;
    hide(): void;
    position(): any;
    getValue(): any;
    setValue(val: any): void;
    serializeValue(): any;
    isValueChanged(): boolean;
    applyValue(item: Item, state: any): void;
    loadValue(item: Item): void;
    validateValue(value: any): any;
    validate(): any;
}
export declare abstract class CellEditor extends Model {
    static initClass(): void;
}
export declare class StringEditorView extends CellEditorView {
    model: StringEditor;
    inputEl: HTMLInputElement;
    readonly emptyValue: string;
    protected _createInput(): HTMLInputElement;
    renderEditor(): void;
    loadValue(item: Item): void;
}
export declare class StringEditor extends CellEditor {
    static initClass(): void;
}
export declare class TextEditorView extends CellEditorView {
    model: TextEditor;
    inputEl: HTMLTextAreaElement;
    protected _createInput(): HTMLTextAreaElement;
}
export declare class TextEditor extends CellEditor {
    static initClass(): void;
}
export declare class SelectEditorView extends CellEditorView {
    model: SelectEditor;
    inputEl: HTMLSelectElement;
    protected _createInput(): HTMLSelectElement;
    renderEditor(): void;
}
export declare class SelectEditor extends CellEditor {
    options: string[];
    static initClass(): void;
}
export declare class PercentEditorView extends CellEditorView {
    model: PercentEditor;
    inputEl: HTMLInputElement;
    protected _createInput(): HTMLInputElement;
}
export declare class PercentEditor extends CellEditor {
    static initClass(): void;
}
export declare class CheckboxEditorView extends CellEditorView {
    model: CheckboxEditor;
    inputEl: HTMLInputElement;
    protected _createInput(): HTMLInputElement;
    renderEditor(): void;
    loadValue(item: Item): void;
    serializeValue(): any;
}
export declare class CheckboxEditor extends CellEditor {
    static initClass(): void;
}
export declare class IntEditorView extends CellEditorView {
    model: IntEditor;
    inputEl: HTMLInputElement;
    protected _createInput(): HTMLInputElement;
    renderEditor(): void;
    remove(): void;
    serializeValue(): any;
    loadValue(item: Item): void;
    validateValue(value: any): any;
}
export declare class IntEditor extends CellEditor {
    static initClass(): void;
}
export declare class NumberEditorView extends CellEditorView {
    model: NumberEditor;
    inputEl: HTMLInputElement;
    protected _createInput(): HTMLInputElement;
    renderEditor(): void;
    remove(): void;
    serializeValue(): any;
    loadValue(item: Item): void;
    validateValue(value: any): any;
}
export declare class NumberEditor extends CellEditor {
    static initClass(): void;
}
export declare class TimeEditorView extends CellEditorView {
    model: TimeEditor;
    inputEl: HTMLInputElement;
    protected _createInput(): HTMLInputElement;
}
export declare class TimeEditor extends CellEditor {
    static initClass(): void;
}
export declare class DateEditorView extends CellEditorView {
    model: DateEditor;
    inputEl: HTMLInputElement;
    protected _createInput(): HTMLInputElement;
    readonly emptyValue: Date;
    renderEditor(): void;
    destroy(): void;
    show(): void;
    hide(): void;
    position(): any;
    getValue(): any;
    setValue(_val: any): void;
}
export declare class DateEditor extends CellEditor {
    static initClass(): void;
}
