"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var box_1 = require("./box");
var ColumnView = /** @class */ (function (_super) {
    tslib_1.__extends(ColumnView, _super);
    function ColumnView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ColumnView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-grid-column");
    };
    return ColumnView;
}(box_1.BoxView));
exports.ColumnView = ColumnView;
var Column = /** @class */ (function (_super) {
    tslib_1.__extends(Column, _super);
    function Column(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this._horizontal = false;
        return _this;
    }
    Column.initClass = function () {
        this.prototype.type = "Column";
        this.prototype.default_view = ColumnView;
    };
    return Column;
}(box_1.Box));
exports.Column = Column;
Column.initClass();
