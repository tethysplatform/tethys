"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var box_1 = require("./box");
var RowView = /** @class */ (function (_super) {
    tslib_1.__extends(RowView, _super);
    function RowView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    RowView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-grid-row");
    };
    return RowView;
}(box_1.BoxView));
exports.RowView = RowView;
var Row = /** @class */ (function (_super) {
    tslib_1.__extends(Row, _super);
    function Row(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this._horizontal = true;
        return _this;
    }
    Row.initClass = function () {
        this.prototype.type = "Row";
        this.prototype.default_view = RowView;
    };
    return Row;
}(box_1.Box));
exports.Row = Row;
Row.initClass();
