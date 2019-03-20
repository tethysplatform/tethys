"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var layout_dom_1 = require("./layout_dom");
var SpacerView = /** @class */ (function (_super) {
    tslib_1.__extends(SpacerView, _super);
    function SpacerView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SpacerView.prototype.render = function () {
        _super.prototype.render.call(this);
        if (this.model.sizing_mode == "fixed") {
            this.el.style.width = this.model.width + "px";
            this.el.style.height = this.model.height + "px";
        }
    };
    SpacerView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-spacer-box");
    };
    // spacer must always have some width/height
    SpacerView.prototype.get_width = function () {
        return 1;
    };
    SpacerView.prototype.get_height = function () {
        return 1;
    };
    return SpacerView;
}(layout_dom_1.LayoutDOMView));
exports.SpacerView = SpacerView;
var Spacer = /** @class */ (function (_super) {
    tslib_1.__extends(Spacer, _super);
    function Spacer(attrs) {
        return _super.call(this, attrs) || this;
    }
    Spacer.initClass = function () {
        this.prototype.type = "Spacer";
        this.prototype.default_view = SpacerView;
    };
    Spacer.prototype.get_constrained_variables = function () {
        return tslib_1.__assign({}, _super.prototype.get_constrained_variables.call(this), { on_edge_align_top: this._top, on_edge_align_bottom: this._height_minus_bottom, on_edge_align_left: this._left, on_edge_align_right: this._width_minus_right, box_cell_align_top: this._top, box_cell_align_bottom: this._height_minus_bottom, box_cell_align_left: this._left, box_cell_align_right: this._width_minus_right, box_equal_size_top: this._top, box_equal_size_bottom: this._height_minus_bottom, box_equal_size_left: this._left, box_equal_size_right: this._width_minus_right });
    };
    return Spacer;
}(layout_dom_1.LayoutDOM));
exports.Spacer = Spacer;
Spacer.initClass();
