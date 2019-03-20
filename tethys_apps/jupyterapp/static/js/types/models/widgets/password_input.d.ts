import { TextInput, TextInputView } from "./text_input";
export declare class PasswordInputView extends TextInputView {
    model: PasswordInput;
    render(): void;
}
export declare namespace PasswordInput {
    interface Attrs extends TextInput.Attrs {
    }
    interface Props extends TextInput.Props {
    }
}
export interface PasswordInput extends PasswordInput.Attrs {
}
export declare class PasswordInput extends TextInput {
    properties: PasswordInput.Props;
    constructor(attrs?: Partial<PasswordInput.Attrs>);
    static initClass(): void;
}
