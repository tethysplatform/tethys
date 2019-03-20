"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var p = require("core/properties");
var dom_1 = require("core/dom");
var dom_view_1 = require("core/dom_view");
var model_1 = require("../../../model");
var data_table_1 = require("./data_table");
var CellEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(CellEditorView, _super);
    function CellEditorView(options) {
        return _super.call(this, tslib_1.__assign({ model: options.column.model }, options)) || this;
    }
    Object.defineProperty(CellEditorView.prototype, "emptyValue", {
        get: function () {
            return null;
        },
        enumerable: true,
        configurable: true
    });
    CellEditorView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.inputEl = this._createInput();
        this.defaultValue = null;
        this.args = options;
        this.render();
    };
    CellEditorView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-cell-editor");
    };
    CellEditorView.prototype.render = function () {
        _super.prototype.render.call(this);
        this.args.container.appendChild(this.el);
        this.el.appendChild(this.inputEl);
        this.renderEditor();
        this.disableNavigation();
    };
    CellEditorView.prototype.renderEditor = function () { };
    CellEditorView.prototype.disableNavigation = function () {
        this.inputEl.addEventListener("keydown", function (event) {
            switch (event.keyCode) {
                case dom_1.Keys.Left:
                case dom_1.Keys.Right:
                case dom_1.Keys.Up:
                case dom_1.Keys.Down:
                case dom_1.Keys.PageUp:
                case dom_1.Keys.PageDown:
                    event.stopImmediatePropagation();
            }
        });
    };
    CellEditorView.prototype.destroy = function () {
        this.remove();
    };
    CellEditorView.prototype.focus = function () {
        this.inputEl.focus();
    };
    CellEditorView.prototype.show = function () { };
    CellEditorView.prototype.hide = function () { };
    CellEditorView.prototype.position = function () { };
    CellEditorView.prototype.getValue = function () {
        return this.inputEl.value;
    };
    CellEditorView.prototype.setValue = function (val) {
        this.inputEl.value = val;
    };
    CellEditorView.prototype.serializeValue = function () {
        return this.getValue();
    };
    CellEditorView.prototype.isValueChanged = function () {
        return !(this.getValue() == "" && this.defaultValue == null) && this.getValue() !== this.defaultValue;
    };
    CellEditorView.prototype.applyValue = function (item, state) {
        this.args.grid.getData().setField(item[data_table_1.DTINDEX_NAME], this.args.column.field, state);
    };
    CellEditorView.prototype.loadValue = function (item) {
        var value = item[this.args.column.field];
        this.defaultValue = value != null ? value : this.emptyValue;
        this.setValue(this.defaultValue);
    };
    CellEditorView.prototype.validateValue = function (value) {
        if (this.args.column.validator) {
            var result = this.args.column.validator(value);
            if (!result.valid) {
                return result;
            }
        }
        return { valid: true, msg: null };
    };
    CellEditorView.prototype.validate = function () {
        return this.validateValue(this.getValue());
    };
    return CellEditorView;
}(dom_view_1.DOMView));
exports.CellEditorView = CellEditorView;
var CellEditor = /** @class */ (function (_super) {
    tslib_1.__extends(CellEditor, _super);
    function CellEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CellEditor.initClass = function () {
        this.prototype.type = "CellEditor";
    };
    return CellEditor;
}(model_1.Model));
exports.CellEditor = CellEditor;
CellEditor.initClass();
var StringEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(StringEditorView, _super);
    function StringEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(StringEditorView.prototype, "emptyValue", {
        get: function () {
            return "";
        },
        enumerable: true,
        configurable: true
    });
    StringEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "text" });
    };
    StringEditorView.prototype.renderEditor = function () {
        //completions = @model.completions
        //if completions.length != 0
        //  @inputEl.classList.add("bk-cell-editor-completion")
        //  $(@inputEl).autocomplete({source: completions})
        //  $(@inputEl).autocomplete("widget")
        this.inputEl.focus();
        this.inputEl.select();
    };
    StringEditorView.prototype.loadValue = function (item) {
        _super.prototype.loadValue.call(this, item);
        this.inputEl.defaultValue = this.defaultValue;
        this.inputEl.select();
    };
    return StringEditorView;
}(CellEditorView));
exports.StringEditorView = StringEditorView;
var StringEditor = /** @class */ (function (_super) {
    tslib_1.__extends(StringEditor, _super);
    function StringEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    StringEditor.initClass = function () {
        this.prototype.type = 'StringEditor';
        this.prototype.default_view = StringEditorView;
        this.define({
            completions: [p.Array, []],
        });
    };
    return StringEditor;
}(CellEditor));
exports.StringEditor = StringEditor;
StringEditor.initClass();
var TextEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(TextEditorView, _super);
    function TextEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TextEditorView.prototype._createInput = function () {
        return dom_1.textarea();
    };
    return TextEditorView;
}(CellEditorView));
exports.TextEditorView = TextEditorView;
var TextEditor = /** @class */ (function (_super) {
    tslib_1.__extends(TextEditor, _super);
    function TextEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TextEditor.initClass = function () {
        this.prototype.type = 'TextEditor';
        this.prototype.default_view = TextEditorView;
    };
    return TextEditor;
}(CellEditor));
exports.TextEditor = TextEditor;
TextEditor.initClass();
var SelectEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(SelectEditorView, _super);
    function SelectEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SelectEditorView.prototype._createInput = function () {
        return dom_1.select();
    };
    SelectEditorView.prototype.renderEditor = function () {
        for (var _i = 0, _a = this.model.options; _i < _a.length; _i++) {
            var opt = _a[_i];
            this.inputEl.appendChild(dom_1.option({ value: opt }, opt));
        }
        this.focus();
    };
    return SelectEditorView;
}(CellEditorView));
exports.SelectEditorView = SelectEditorView;
var SelectEditor = /** @class */ (function (_super) {
    tslib_1.__extends(SelectEditor, _super);
    function SelectEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SelectEditor.initClass = function () {
        this.prototype.type = 'SelectEditor';
        this.prototype.default_view = SelectEditorView;
        this.define({
            options: [p.Array, []],
        });
    };
    return SelectEditor;
}(CellEditor));
exports.SelectEditor = SelectEditor;
SelectEditor.initClass();
var PercentEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(PercentEditorView, _super);
    function PercentEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PercentEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "text" });
    };
    return PercentEditorView;
}(CellEditorView));
exports.PercentEditorView = PercentEditorView;
var PercentEditor = /** @class */ (function (_super) {
    tslib_1.__extends(PercentEditor, _super);
    function PercentEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    PercentEditor.initClass = function () {
        this.prototype.type = 'PercentEditor';
        this.prototype.default_view = PercentEditorView;
    };
    return PercentEditor;
}(CellEditor));
exports.PercentEditor = PercentEditor;
PercentEditor.initClass();
var CheckboxEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(CheckboxEditorView, _super);
    function CheckboxEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CheckboxEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "checkbox", value: "true" });
    };
    CheckboxEditorView.prototype.renderEditor = function () {
        this.focus();
    };
    CheckboxEditorView.prototype.loadValue = function (item) {
        this.defaultValue = !!item[this.args.column.field];
        this.inputEl.checked = this.defaultValue;
    };
    CheckboxEditorView.prototype.serializeValue = function () {
        return this.inputEl.checked;
    };
    return CheckboxEditorView;
}(CellEditorView));
exports.CheckboxEditorView = CheckboxEditorView;
var CheckboxEditor = /** @class */ (function (_super) {
    tslib_1.__extends(CheckboxEditor, _super);
    function CheckboxEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    CheckboxEditor.initClass = function () {
        this.prototype.type = 'CheckboxEditor';
        this.prototype.default_view = CheckboxEditorView;
    };
    return CheckboxEditor;
}(CellEditor));
exports.CheckboxEditor = CheckboxEditor;
CheckboxEditor.initClass();
var IntEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(IntEditorView, _super);
    function IntEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    IntEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "text" });
    };
    IntEditorView.prototype.renderEditor = function () {
        //$(@inputEl).spinner({step: @model.step})
        this.inputEl.focus();
        this.inputEl.select();
    };
    IntEditorView.prototype.remove = function () {
        //$(@inputEl).spinner("destroy")
        _super.prototype.remove.call(this);
    };
    IntEditorView.prototype.serializeValue = function () {
        return parseInt(this.getValue(), 10) || 0;
    };
    IntEditorView.prototype.loadValue = function (item) {
        _super.prototype.loadValue.call(this, item);
        this.inputEl.defaultValue = this.defaultValue;
        this.inputEl.select();
    };
    IntEditorView.prototype.validateValue = function (value) {
        if (isNaN(value))
            return { valid: false, msg: "Please enter a valid integer" };
        else
            return _super.prototype.validateValue.call(this, value);
    };
    return IntEditorView;
}(CellEditorView));
exports.IntEditorView = IntEditorView;
var IntEditor = /** @class */ (function (_super) {
    tslib_1.__extends(IntEditor, _super);
    function IntEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    IntEditor.initClass = function () {
        this.prototype.type = 'IntEditor';
        this.prototype.default_view = IntEditorView;
        this.define({
            step: [p.Number, 1],
        });
    };
    return IntEditor;
}(CellEditor));
exports.IntEditor = IntEditor;
IntEditor.initClass();
var NumberEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(NumberEditorView, _super);
    function NumberEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    NumberEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "text" });
    };
    NumberEditorView.prototype.renderEditor = function () {
        //$(@inputEl).spinner({step: @model.step})
        this.inputEl.focus();
        this.inputEl.select();
    };
    NumberEditorView.prototype.remove = function () {
        //$(@inputEl).spinner("destroy")
        _super.prototype.remove.call(this);
    };
    NumberEditorView.prototype.serializeValue = function () {
        return parseFloat(this.getValue()) || 0.0;
    };
    NumberEditorView.prototype.loadValue = function (item) {
        _super.prototype.loadValue.call(this, item);
        this.inputEl.defaultValue = this.defaultValue;
        this.inputEl.select();
    };
    NumberEditorView.prototype.validateValue = function (value) {
        if (isNaN(value))
            return { valid: false, msg: "Please enter a valid number" };
        else
            return _super.prototype.validateValue.call(this, value);
    };
    return NumberEditorView;
}(CellEditorView));
exports.NumberEditorView = NumberEditorView;
var NumberEditor = /** @class */ (function (_super) {
    tslib_1.__extends(NumberEditor, _super);
    function NumberEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    NumberEditor.initClass = function () {
        this.prototype.type = 'NumberEditor';
        this.prototype.default_view = NumberEditorView;
        this.define({
            step: [p.Number, 0.01],
        });
    };
    return NumberEditor;
}(CellEditor));
exports.NumberEditor = NumberEditor;
NumberEditor.initClass();
var TimeEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(TimeEditorView, _super);
    function TimeEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TimeEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "text" });
    };
    return TimeEditorView;
}(CellEditorView));
exports.TimeEditorView = TimeEditorView;
var TimeEditor = /** @class */ (function (_super) {
    tslib_1.__extends(TimeEditor, _super);
    function TimeEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TimeEditor.initClass = function () {
        this.prototype.type = 'TimeEditor';
        this.prototype.default_view = TimeEditorView;
    };
    return TimeEditor;
}(CellEditor));
exports.TimeEditor = TimeEditor;
TimeEditor.initClass();
var DateEditorView = /** @class */ (function (_super) {
    tslib_1.__extends(DateEditorView, _super);
    function DateEditorView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DateEditorView.prototype._createInput = function () {
        return dom_1.input({ type: "text" });
    };
    Object.defineProperty(DateEditorView.prototype, "emptyValue", {
        get: function () {
            return new Date();
        },
        enumerable: true,
        configurable: true
    });
    DateEditorView.prototype.renderEditor = function () {
        //this.calendarOpen = false
        //@$datepicker = $(@inputEl).datepicker({
        //  showOn: "button"
        //  buttonImageOnly: true
        //  beforeShow: () => @calendarOpen = true
        //  onClose: () => @calendarOpen = false
        //})
        //@$datepicker.siblings(".ui-datepicker-trigger").css("vertical-align": "middle")
        //@$datepicker.width(@$datepicker.width() - (14 + 2*4 + 4)) # img width + margins + edge distance
        this.inputEl.focus();
        this.inputEl.select();
    };
    DateEditorView.prototype.destroy = function () {
        //$.datepicker.dpDiv.stop(true, true)
        //@$datepicker.datepicker("hide")
        //@$datepicker.datepicker("destroy")
        _super.prototype.destroy.call(this);
    };
    DateEditorView.prototype.show = function () {
        //if @calendarOpen
        //  $.datepicker.dpDiv.stop(true, true).show()
        _super.prototype.show.call(this);
    };
    DateEditorView.prototype.hide = function () {
        //if @calendarOpen
        //  $.datepicker.dpDiv.stop(true, true).hide()
        _super.prototype.hide.call(this);
    };
    DateEditorView.prototype.position = function ( /*_position*/) {
        //if @calendarOpen
        //  $.datepicker.dpDiv.css(top: position.top + 30, left: position.left)
        return _super.prototype.position.call(this);
    };
    DateEditorView.prototype.getValue = function () { };
    //return @$datepicker.datepicker("getDate").getTime()
    DateEditorView.prototype.setValue = function (_val) { };
    return DateEditorView;
}(CellEditorView));
exports.DateEditorView = DateEditorView;
//@$datepicker.datepicker("setDate", new Date(val))
var DateEditor = /** @class */ (function (_super) {
    tslib_1.__extends(DateEditor, _super);
    function DateEditor() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DateEditor.initClass = function () {
        this.prototype.type = 'DateEditor';
        this.prototype.default_view = DateEditorView;
    };
    return DateEditor;
}(CellEditor));
exports.DateEditor = DateEditor;
DateEditor.initClass();
